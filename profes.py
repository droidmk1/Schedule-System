#Logica en python para gestionar el sistema de horarios (formato 24hr)
import pandas as pd
import numpy as np

inicioClases=8
finClases=23

'''Array de dias con horas'''
dias=['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
horas=list(range(inicioClases,finClases+1))

'''Creacion de horario vacio bajo los parametros establecidos'''
horario = np.full([np.size(horas),np.size(dias)], None)

df_profes=pd.DataFrame(horario,index=horas,columns=dias)
#Alejandro A.
df_profes['Lunes']=np.where((df_profes.index >= 6) & (df_profes.index <= 9), 'Alejandro A.', df_profes['Lunes'])
df_profes['Lunes']=np.where((df_profes.index >= 6) & (df_profes.index <= 9), 'Alejandro A.', df_profes['Lunes'])

#Huallipe A.
df_profes['Lunes']=np.where((df_profes.index == 9), df_profes['Lunes'][9] + '| Carlo H.', df_profes['Lunes'])
df_profes['Martes']=np.where((df_profes.index == 9), 'Carlo H.', df_profes['Martes'])

#Alvaro F.
df_profes['Jueves']=np.where((df_profes.index >= 0) & (df_profes.index <= len(horas)+inicioClases), 'Alvaro F.', df_profes['Jueves'])

#Alvaro F.
df_profes['Jueves']=np.where((df_profes.index >= 0) & (df_profes.index <= len(horas)+inicioClases), 'Alvaro F.', df_profes['Viernes'])
print(df_profes)