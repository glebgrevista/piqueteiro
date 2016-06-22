# piqueteiro
piqueteiro é uma pequena aplicação escrita em python que, dada uma lista de códigos numéricos de cursos da unicamp em greve, produz um arquivo csv com todas as aulas do curso em uma semana, incluindo o percentual de alunos em greve em cada uma delas.

#Exemplo de uso:
Entrada: 

piqueteiro.py 4,40,51,108

Saída:

Dia,Hora,Sala,Matéria,Turma,Alunos em Greve,Alunos,Proporção
Seg,10:00,CB02,F 128,A,74,74,100.00
Qua,10:00,CB08,F 128,A,74,74,100.00
Seg,10:00,CB02,F 128,B,72,72,100.00
Qua,10:00,CB09,F 128,B,72,72,100.00
Seg,10:00,CB08,F 128,D,1,67,1.49
Qua,10:00,CB02,F 128,D,1,67,1.49
Seg,10:00,CB03,F 128,G,4,70,5.71
Qua,10:00,CB15,F 128,G,4,70,5.71
Seg,10:00,CB03,F 128,J,2,57,3.51
Qua,10:00,CB14,F 128,J,2,57,3.51
Seg,10:00,CB09,F 128,K,1,64,1.56
Qua,10:00,CB01,F 128,K,1,64,1.56
Seg,10:00,CB15,F 128,L,6,65,9.23
Qua,10:00,CB01,F 128,L,6,65,9.23
...
