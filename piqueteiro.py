#!/usr/bin/env python3
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
from sys import argv, exit
import time
import os

if argv[1] == '-h' or argv[1] == '-H' or argv[1] == '--help':
    ajuda()
try:
    cursos_greve = argv[1].split(',')
except IndexError:
    ajuda()

browser = webdriver.Firefox()

#armazena disciplinas e turmas já obtidas no arquivo temp.txt
temp_exists = os.path.isfile('temp.txt')
done_discs = []
done_t = []
mode = 'w'
if temp_exists:
    with open('temp.txt', mode='r') as file:
        for line in file:
            disc, turma = line.split(',')
            done_discs.append(disc)
            done_t.append(turma)

print_csv(cursos_greve)
browser.close()


def print_csv(cursos_greve):
    """
    imprime na tela, separados por vírgula, dia, hora, sala, matéria, turma, alunos em greve, 
    alunos e percentual em greve para todas as aulas de todas as disciplinas dos cursos em cursos_greve. 
    cursos_greve deve ser uma lista de strings, cada uma contendo o código de uma disciplina da Unicamp.
    """
    cursos = get_disc(cursos_greve)
    if not temp_exists:
        print('Dia,Hora,Sala,Matéria,Turma,Alunos em Greve,Alunos,Percentual em greve')
    with open('temp.txt', mode='a') as file:
        for disc in cursos:
            raw_resp = get_search(disc)
            soup = bs(raw_resp, 'html.parser')
            #a parte a seguir é meio críptica sem ver o código fonte: vale a pena inspecionar
            #a pesquisa em http://www.dac.unicamp.br/sistemas/horarios/grad/busca/procura.php
            #no navegador
            for tag in soup.find_all('b'):
                text = str(tag.string)
                if 'Turma:' in text:
                    tag = tag.next_element
                    turma = str(tag.next_element)
                    turma = turma.split()[0]
                    if turma in done_t:
                        continue
                    proporcao, grevistas, total = get_proportion(disc, turma, cursos_greve)
                elif 'Horário:' in text:
                    if turma in done_t:
                        continue
                    try:
                        old_tag = tag
                        tag = tag.find_next_sibling('table')
                        tab_lines = tag('td')
                        tab_lines = tab_lines[1:]
                    except:
                        tag = old_tag
                        n_tag = tag.next_element
                        n_tag = n_tag.next_element
                        if 'Horário não informado' in str(n_tag):
                            pass     #disciplina não tem os horários informados (talvez sequer seja presencial)
                        else:
                            print('Erro ao buscar horários para', disc, turma)
                            #print(soup.prettify())
                            exit()
                    else:
                        for line in tab_lines:
                            hor_str = line.string.split('\n')
                            dia = hor_str[0][:-1]
                            hor_str = hor_str[1].split('/')
                            hora = hor_str[0]
                            sala = hor_str[1]
                            if proporcao > 0.00:
                                print(dia, hora, sala, disc, turma, grevistas, total, "%.2f" %proporcao, sep=',')
                                print(disc, turma, file=file, sep=',')
    
def get_disc(c_list):
    """
    retorna lista com o código das disciplinas constantes no currículo da dac para os cursos da lista c_list.
    c_list deve ser uma lista de strings, sendo cada string o código numérico válido de um curso da Unicamp.
    """
    template_url = "http://www.dac.unicamp.br/sistemas/catalogos/grad/catalogo2016/curriculoPleno/cp"
    discs = []
    for course in c_list:
        url = template_url + course + '.html'
        raw_resp = requests.get(url)
        soup = bs(raw_resp.text, 'html.parser')
        for link in soup.find_all('a'):
            url = link['href']
            if '../coordenadorias/' in url:
                disc = url[-5:]
                if disc not in done_discs:
                    discs.append(disc)
    return discs

def get_proportion(disc, turma, cursos_greve):
    """
    calcula total, o número total de alunos da disciplina disc turma turma, em_greve, o número de alunos em greve da mesma e perc,
    o percentual de alunos em greve da disciplina.
    retorna a tupla perc, em_greve, total
    """
    source = get_page(disc, turma)
    soup = bs(source)
    tabs = soup("table")[8]('tr')[2:]
    tab_list = [line('td')[3].text for line in tabs]
    total = 0
    em_greve = 0
    for line in tab_list:
        total += 1
        if line in cursos_greve:
            em_greve += 1
    perc = em_greve * 100.0 / total
    return perc, em_greve, total

def get_search(disc):
    """
    retorna código fonte da busca por oferecimentos da disciplina disc em http://www.dac.unicamp.br/sistemas/horarios/grad/busca/procura.php
    """
    template_busca = 'http://www.dac.unicamp.br/sistemas/horarios/grad/busca/procura.php?teste=1&nome='
    busca = template_busca + disc
    browser.get(busca)
    source = browser.page_source
    return source

def get_page(disc, turma):
    """
    retorna código fonte da busca por alunos da disciplina disc e turma turma em http://www.daconline.unicamp.br/altmatr/menupublico.do#
    """
    site = 'http://www.daconline.unicamp.br/altmatr/menupublico.do#'
    browser.get(site)
    browser.find_elements_by_class_name('linkmenu')[1].click()
    main_w = browser.window_handles[0]
    browser.switch_to_window(browser.window_handles[1])
    time.sleep(1)
    select = Select(browser.find_element_by_xpath('//select[@name="cboSubG"]'))
    select.select_by_visible_text('1º Semestre')
    browser.find_element_by_xpath('//input[@name="txtDisciplina"]').send_keys(disc)
    browser.find_element_by_xpath('//input[@name="txtTurma"]').send_keys(turma)
    browser.find_element_by_xpath('//input[@type="submit"]').click()
    source = browser.page_source
    browser.close()
    browser.switch_to_window(main_w)
    return source

def ajuda():
    print('Uso:', argv[0], 'CURSOS_EM_GREVE')
    print('Imprime dia, hora, sala, nome, turma e proporção percentual de alunos em greve para todas as matérias dos CURSOS_EM_GREVE.')
    