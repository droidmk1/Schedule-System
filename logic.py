#Logica en python para gestionar el sistema de horarios (formato 24hr)
import pandas as pd
import numpy as np

'''Decorador e identificacion para el horario'''
# print('Facultad: ')
# facultad=input()

# print('Año: ')
# año=input()

# print('Carrera: ')
# carrera=input()

'''Array de Datos Cursos y Horas para cada curso'''
cursos=['Estadistica', 'Sistema Operativos', 'Metodos Numericos', 'Analisis Funcional', 'Tecnicas de Modelamiento']
horaCursos=[8, 7, 6, 6, 6]

'''Rango de horas para clases en el dia'''
# print('Hora inicio de clases: ')
# inicioClases=input()
# inicioClases=int(inicioClases)
# print('Hora fin de clases: ')
# finClases=input()
# finClases=int(finClases)

inicioClases=8
finClases=21

'''Rango de horas para el almuerzo (2hr Generalmente)'''
# print('Hora inicio almuerzo: ')
# inicioAlmuerzo=input()
# inicioAlmuerzo=int(inicioAlmuerzo)
# print('Hora fin almuerzo: ')
# finAlmuerzo=input()
# finAlmuerzo=int(finAlmuerzo)

inicioAlmuerzo=12
finAlmuerzo=14

almuerzo=list(range(inicioAlmuerzo,finAlmuerzo))

'''Array de dias con horas'''
dias=['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
horas=list(range(inicioClases,finClases+1))

# print(dias)
# print(horas)

'''Creacion de horario vacio bajo los parametros establecidos'''
horario = np.full([np.size(horas),np.size(dias)], None)
# print(horario)

'''Vista Previa del Horario en pandas dataframe'''
df_horario=pd.DataFrame(horario,index=horas,columns=dias)
# print(df)

'''Modificacion del dataframe (Agregando datos)'''
for i in range(np.size(almuerzo)):
    df_horario.iloc[almuerzo[i]-inicioClases] = 'Receso'

j=0

for i in range(np.size(cursos)):
    if horaCursos[i] > 4 and df_horario.iloc[i][j] != 'Receso':
        df_horario.iloc[i][j] = cursos[i]
        df_horario.iloc[i][j+1] = cursos[i]
        j=j+1

# print(f'\nHorario para la facultad {facultad} carrera de {carrera} del año {año}\n')
# print(df_horario)

'''Profesores Disponibilidad'''
profesores=['Alvaro F.', 'Alejandro A.','Carlo H.','Carlos C.','Freddy C.']
disponibilidad=[list(range(inicioClases,finClases+1))]

'''Creacion de horario profes vacio bajo los parametros establecidos'''
profes = np.full([np.size(disponibilidad),np.size(profesores)], 'N. D.')
# print(horario)

'''Vista Previa del Horario de profes en pandas dataframe'''
df_profes_Alejandro=pd.DataFrame(horario,index=horas,columns=dias)
df_profes_Alejandro['Lunes']=np.where((df_profes_Alejandro.index >= 6) & (df_profes_Alejandro.index <= 9), 'Alejandro A.', df_profes_Alejandro['Lunes'])
df_profes_Alejandro['Martes']='Alejandro A.'
df_profes_Alejandro['Miercoles']=np.where((df_profes_Alejandro.index >= 14) & (df_profes_Alejandro.index <= 17), 'Alejandro A.', df_profes_Alejandro['Miercoles'])
df_profes_Alejandro['Jueves']='Alejandro A.'
df_profes_Alejandro['Viernes']='Alejandro A.'
df_profes_Alejandro['Sabado']=np.where((df_profes_Alejandro.index >= 10) & (df_profes_Alejandro.index <= 15), 'Alejandro A.', df_profes_Alejandro['Sabado'])
df_profes_Alejandro['Domingo']='Alejandro A.'

print(df_profes_Alejandro)


df_profes_Carlos=pd.DataFrame(horario,index=horas,columns=dias)
df_profes_Carlos['Lunes']=np.where((df_profes_Carlos.index >= 13) & (df_profes_Carlos.index <= 16), 'Carlos C.', df_profes_Carlos['Lunes'])
df_profes_Carlos['Martes']='Carlos C.'
df_profes_Carlos['Miercoles']=np.where((df_profes_Carlos.index >= 15) & (df_profes_Carlos.index <= 19), 'Carlos C.', df_profes_Carlos['Miercoles'])
df_profes_Carlos['Jueves']=np.where((df_profes_Carlos.index >= 15) & (df_profes_Carlos.index <= 19), 'Carlos C.', df_profes_Carlos['Jueves'])
df_profes_Carlos['Domingo']=np.where((df_profes_Carlos.index >= 18) & (df_profes_Carlos.index <= 20), 'Carlos C.', df_profes_Carlos['Jueves'])

print(df_profes_Carlos)