from hashlib import md5
from tkinter import NONE
from flask import Flask, render_template, request, redirect, url_for, flash, session
from random import randrange
from datetime import datetime
import uuid
import pandas as pd
import numpy as np

# bigquery
import os
from google.cloud import bigquery

miProyecto = ''
bq = ''


def conexionBigQuery():
    global miProyecto, ruta_key

    miProyecto = 'unmsm-horarios'
    print('ruta')
    ruta_key = 'horarios-unmsm.json'

    try:
        if (os.environ['GOOGLE_APPLICATION_CREDENTIALS']):
            print('La variable de entorno existe')
    except Exception as e:
        print('La variable de entorno no existe')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(ruta_key)
        print('Se creo la variable de entorno')

    try:
        global bq
        bq = bigquery.Client(miProyecto)
        sql = """select true as conexion"""
        df = bq.query(sql).result().to_dataframe()

        if df['conexion'][0] == True:
            print('Estamos conectados a BigQuery')
        else:
            print('Algo paso pero no nos pudimos conectar')

    except Exception as e:
        print('[ERROR]: ', str(e))


conexionBigQuery()

# fin bigquery

app = Flask(__name__)

# settings
app.secret_key = 'mysecretkey'


@app.route('/', methods=['GET', 'POST'])
def home():
    # CheckLoginInSession
    if request.method == 'POST':
        session.clear()
        session['usuario'] = request.form['login-email']
        session.permanent = True
        # CheckData()
        print('soy el usuario', session['usuario'])
    return render_template('home.html')


@app.route('/system')
def system():
    return render_template('system.html')


@app.route('/horarios')
def horarios():
    return render_template('horarios.html')


@app.route('/profesores')
def profesores():
    return render_template('profesores.html')


@app.route('/profes_dispo')
def profes_dispo():
    # sql = f'''
    # 	SELECT Id_curso, Nombre FROM `unmsm-horarios.db_horario.cursos`
    # '''
    # df = bq.query(sql).result().to_dataframe()
    # df = df.to_dict('r')
    # print(df)
    return render_template('profes_dispo.html')


@app.route('/profes_disponibilidad', methods=['POST'])
def profes_disponibilidad():
    if request.method == 'POST':
        Id_profe = str(uuid.uuid4())
        Codigo = request.form['codigo']
        nombre = request.form['nombre']
        posiciones = np.arange(8, 23)
        lunes = [None]*14
        martes = [None]*14
        miercoles = [None]*14
        jueves = [None]*14
        viernes = [None]*14
        sabado = [None]*14
        domingo = [None]*14

        print('Profesor: ', nombre)
        for key, val in request.form.items():
            if key.startswith("L"):
                index_lunes = val.split('_')
                index_lunes = index_lunes[1]
                pos_lunes = np.where(posiciones == int(index_lunes))
                pos_lunes = int(pos_lunes[0][0])
                lunes[pos_lunes] = val

            elif key.startswith("Mi"):
                index_miercoles = val.split('_')
                index_miercoles = index_miercoles[1]
                pos_miercoles = np.where(posiciones == int(index_miercoles))
                pos_miercoles = int(pos_miercoles[0][0])
                miercoles[pos_miercoles] = val

            elif key.startswith("M"):
                index_martes = val.split('_')
                index_martes = index_martes[1]
                pos_martes = np.where(posiciones == int(index_martes))
                pos_martes = int(pos_martes[0][0])
                martes[pos_martes] = val

            elif key.startswith("J"):
                index_jueves = val.split('_')
                index_jueves = index_jueves[1]
                pos_jueves = np.where(posiciones == int(index_jueves))
                pos_jueves = int(pos_jueves[0][0])
                jueves[pos_jueves] = val

            elif key.startswith("V"):
                index_viernes = val.split('_')
                index_viernes = index_viernes[1]
                pos_viernes = np.where(posiciones == int(index_viernes))
                pos_viernes = int(pos_viernes[0][0])
                viernes[pos_viernes] = val

            elif key.startswith("S"):
                index_sabado = val.split('_')
                index_sabado = index_sabado[1]
                pos_sabado = np.where(posiciones == int(index_sabado))
                pos_sabado = int(pos_sabado[0][0])
                sabado[pos_sabado] = val

        df_profes_disponibilidad = pd.DataFrame({
            'Id_profe': Id_profe,
            'Lunes': lunes,
            'Martes': martes,
            'Miercoles': miercoles,
            'Jueves': jueves,
            'Viernes': viernes,
            'Sabado': sabado,
            'Domingo': domingo
        })

        print(df_profes_disponibilidad)
        df_profes_disponibilidad.to_gbq(
            'db_horario.profes_disponibilidad', project_id=miProyecto, if_exists='append')

        sql = f'''
			INSERT INTO `unmsm-horarios.db_horario.profes` (`id_profe`,`Nombre`,`Codigo`) VALUES ('{Id_profe}','{nombre}','{Codigo}')
        '''
        bq.query(sql).result()

    return render_template('profes_dispo.html')


@app.route('/verProfesores')
def verProfesores():
    sql = df_profes_sql()
    df_profes = bq.query(sql).result().to_dataframe()
    df_profes = df_profes.to_dict('r')
    print(df_profes)
    return render_template('verProfesores.html', df_profes=df_profes)


@app.route('/verHorarios')
def verHorarios():
    return render_template('verHorarios.html')


@app.route('/crearHorarios')
def crearHorarios():
    return render_template('crearHorarios.html')


def df_cursos_sql(ciclo):
    sql = f"""
		SELECT Id_curso, Nombre, Ciclo, HT, HP, HL FROM `unmsm-horarios.db_horario.cursos` WHERE Ciclo = '{ciclo}'
		"""
    cursos = bq.query(sql).result().to_dataframe()
    return cursos


def df_profes_sql():
	sql = f"""
		SELECT Id_profe, Nombre, Codigo FROM `unmsm-horarios.db_horario.profes`
	"""
	return sql

@app.route('/make_scheadule', methods=['POST'])
def make_scheadule():
    if request.method == 'POST':
        ciclo = request.form['ciclo']
        session['ciclo'] = ciclo
        # print('\n\n\n\n\nciclo: ', ciclo)
        df = df_cursos_sql(f'{ciclo}')
        df = df.to_dict('r')
        sql = df_profes_sql()
        df_profes = bq.query(sql).result().to_dataframe()
        df_profes = df_profes.to_dict('r')
        print('soy los profes por ciclo: \n', df_profes)
        return render_template('make_scheadule.html', df=df, df1=df_profes)


@app.route('/final_horario', methods=['POST'])
def final_horario():
    if request.method == 'POST':
        n_cursos = []
        n_teoria = []
        n_practica = []
        n_labo = []
        i = 0
        for key, val in request.form.items():
            j = i
            key_split = key.split('_')
            key_curso = key_split[0]
            curso = key_curso
            if curso in n_cursos:
                print('se encontre en el array')
            else:
                n_cursos.append(curso)
                laboratorio = ''
                n_labo.append(laboratorio)
            # print('Curso:', key_curso)

            if key.endswith('_teoria'):
                teoria = val
                # print('Profe Teoria: ', val)
                n_teoria.append(teoria)
                i = i + 1

            elif key.endswith('_practica'):
                practica = val
                # print('Profe Practica: ', val)
                n_practica.append(practica)

            elif key.endswith('_laboratorio'):
                laboratorio = val.split('_')
                laboratorio = laboratorio[0]
                # print('Profe Laboratorio: ', laboratorio)
                n_labo[j-1] = laboratorio

                # print(n_cursos)
                # print(n_teoria)
                # print(n_practica)
                # print(n_labo)
        df_horario_profes_curso = pd.DataFrame({
            'Id_curso': n_cursos,
            'teoria': n_teoria,
            'practica': n_practica,
            'laboratorio': n_labo
        })

        df_horario_profes_curso['laboratorio'] = df_horario_profes_curso['laboratorio'].replace([''], None)

        # print(df_horario_profes_curso)
        # Horario_final(df_horario_profes_curso)
        Horario_final(df_horario_profes_curso)
        messages = "Horario Creado con Exito"
        return render_template('horarios.html', messages=messages)

def Horario_final(profes_curso):
		# print(profes_curso)
		ciclo = session['ciclo']
		df_profes_curso = profes_curso
		df_datos_curso = df_cursos_sql(f'{ciclo}')
		sql = f"""
		SELECT Id_profe, Lunes, Martes, Miercoles, Jueves, Viernes, Sabado FROM `unmsm-horarios.db_horario.profes_disponibilidad`
		"""
		profes_dispo = bq.query(sql).result().to_dataframe()
		df_datos_curso = df_datos_curso[['Id_curso','HT','HP','HL']]
		print(df_datos_curso)
		df_horario_final = pd.DataFrame({
			# 'Horas': ['8_9', '9_10', '10_11', '11_12', '12_13', '13_14', '14_15', '15_16', '16_17', '17_18', '18_19', '19_20', '20_21', '21_22'],
			'Curso':[],
			'Profesor': [],
			'Lunes': [],
			'Martes': [],
			'Miercoles': [],
			'Jueves': [],
			'Viernes': [],
			'Sabado': []
		})

		'''TEORIA'''
		'''Lunes - Teoria'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe teoria por curso: ', df_profes_curso['teoria'][i])
			hrs_teoria = df_datos_curso['HT'][i]

			print('Horas: ', hrs_teoria)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['teoria'][i]]
			Lunes = profes_dispo_recortado['Lunes']
			# print(profes_dispo_recortado)
			Lunes_array = Lunes.dropna().to_numpy()
			# print('Lunes: ', Lunes_array)

			lunes_corto = []

			for j in range(len(Lunes_array)):
				Existe = Lunes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Lunes_array) >= hrs_teoria, hrs_teoria != 0)
				if Existe == False and len(lunes_corto) < hrs_teoria and hrs_teoria != 0:
					lunes_corto.append(Lunes_array[j])

			df_horario_lunes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i],'Profesor': df_profes_curso['teoria'][i], 'Lunes': lunes_corto})
			df_horario_final = df_horario_final.append(df_horario_lunes, ignore_index=True)
			df_datos_curso['HT'][i] = hrs_teoria - len(lunes_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Martes - Teoria'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe teoria por curso: ', df_profes_curso['teoria'][i])
			hrs_teoria = df_datos_curso['HT'][i]

			print('Horas: ', hrs_teoria)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['teoria'][i]]
			Martes = profes_dispo_recortado['Martes']
			# print(profes_dispo_recortado)
			Martes_array = Martes.dropna().to_numpy()
			# print('Martes: ', Martes_array)

			Martes_corto = []

			for j in range(len(Martes_array)):
				Existe = Martes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Martes_array) >= hrs_teoria, hrs_teoria != 0)
				if Existe == False and len(Martes_corto) < hrs_teoria and hrs_teoria != 0:
					Martes_corto.append(Martes_array[j])

			df_horario_Martes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i],'Profesor': df_profes_curso['teoria'][i], 'Martes': Martes_corto})
			df_horario_final = df_horario_final.append(df_horario_Martes, ignore_index=True)
			df_datos_curso['HT'][i] = hrs_teoria - len(Martes_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Miercoles - Teoria'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe teoria por curso: ', df_profes_curso['teoria'][i])
			hrs_teoria = df_datos_curso['HT'][i]

			print('Horas: ', hrs_teoria)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['teoria'][i]]
			Miercoles = profes_dispo_recortado['Miercoles']
			# print(profes_dispo_recortado)
			Miercoles_array = Miercoles.dropna().to_numpy()
			# print('Miercoles: ', Miercoles_array)

			Miercoles_corto = []

			for j in range(len(Miercoles_array)):
				Existe = Miercoles_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Miercoles_array) >= hrs_teoria, hrs_teoria != 0)
				if Existe == False and len(Miercoles_corto) < hrs_teoria and hrs_teoria != 0:
					Miercoles_corto.append(Miercoles_array[j])

			df_horario_Miercoles = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i],'Profesor': df_profes_curso['teoria'][i], 'Miercoles': Miercoles_corto})
			df_horario_final = df_horario_final.append(df_horario_Miercoles, ignore_index=True)
			df_datos_curso['HT'][i] = hrs_teoria - len(Miercoles_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Jueves - Teoria'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe teoria por curso: ', df_profes_curso['teoria'][i])
			hrs_teoria = df_datos_curso['HT'][i]

			print('Horas: ', hrs_teoria)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['teoria'][i]]
			Jueves = profes_dispo_recortado['Jueves']
			# print(profes_dispo_recortado)
			Jueves_array = Jueves.dropna().to_numpy()
			# print('Jueves: ', Jueves_array)

			Jueves_corto = []

			for j in range(len(Jueves_array)):
				Existe = Jueves_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Jueves_array) >= hrs_teoria, hrs_teoria != 0)
				if Existe == False and len(Jueves_corto) < hrs_teoria and hrs_teoria != 0:
					Jueves_corto.append(Jueves_array[j])

			df_horario_Jueves = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i],'Profesor': df_profes_curso['teoria'][i], 'Jueves': Jueves_corto})
			df_horario_final = df_horario_final.append(df_horario_Jueves, ignore_index=True)
			df_datos_curso['HT'][i] = hrs_teoria - len(Jueves_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Viernes - Teoria'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe teoria por curso: ', df_profes_curso['teoria'][i])
			hrs_teoria = df_datos_curso['HT'][i]

			print('Horas: ', hrs_teoria)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['teoria'][i]]
			Viernes = profes_dispo_recortado['Viernes']
			# print(profes_dispo_recortado)
			Viernes_array = Viernes.dropna().to_numpy()
			# print('Viernes: ', Viernes_array)

			Viernes_corto = []

			for j in range(len(Viernes_array)):
				Existe = Viernes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Viernes_array) >= hrs_teoria, hrs_teoria != 0)
				if Existe == False and len(Viernes_corto) < hrs_teoria and hrs_teoria != 0:
					Viernes_corto.append(Viernes_array[j])

			df_horario_Viernes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i],'Profesor': df_profes_curso['teoria'][i], 'Viernes': Viernes_corto})
			df_horario_final = df_horario_final.append(df_horario_Viernes, ignore_index=True)
			df_datos_curso['HT'][i] = hrs_teoria - len(Viernes_corto)
			# print('previa del horario final: \n', df_horario_final)

		print('Tabla del horario final - teoria previa: ')
		print(df_horario_final)

		'''PRACTICA'''
		'''Viernes - Practica'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe practica por curso: ', df_profes_curso['practica'][i])
			hrs_practica = df_datos_curso['HP'][i]

			# print('Horas: ', hrs_practica)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['practica'][i]]
			Viernes = profes_dispo_recortado['Viernes']
			# print(profes_dispo_recortado)
			Viernes_array = Viernes.dropna().to_numpy()
			# print('Viernes: ', Viernes_array)

			Viernes_corto = []

			for j in range(len(Viernes_array)):
				Existe = Viernes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Viernes_array) >= hrs_practica, hrs_practica != 0)
				if Existe == False and len(Viernes_corto) < hrs_practica and hrs_practica != 0:
					Viernes_corto.append(Viernes_array[j])

			df_horario_Viernes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['practica'][i], 'Viernes': Viernes_corto})
			df_horario_final = df_horario_final.append(df_horario_Viernes, ignore_index=True)
			df_datos_curso['HP'][i] = hrs_practica - len(Viernes_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Jueves - Practica'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe practica por curso: ', df_profes_curso['practica'][i])
			hrs_practica = df_datos_curso['HP'][i]

			# print('Horas: ', hrs_practica)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['practica'][i]]
			Jueves = profes_dispo_recortado['Jueves']
			# print(profes_dispo_recortado)
			Jueves_array = Jueves.dropna().to_numpy()
			# print('Jueves: ', Jueves_array)

			Jueves_corto = []

			for j in range(len(Jueves_array)):
				Existe = Jueves_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Jueves_array) >= hrs_practica, hrs_practica != 0)
				if Existe == False and len(Jueves_corto) < hrs_practica and hrs_practica != 0:
					Jueves_corto.append(Jueves_array[j])

			df_horario_Jueves = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['practica'][i], 'Jueves': Jueves_corto})
			df_horario_final = df_horario_final.append(df_horario_Jueves, ignore_index=True)
			df_datos_curso['HP'][i] = hrs_practica - len(Jueves_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Miercoles - Practica'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe practica por curso: ', df_profes_curso['practica'][i])
			hrs_practica = df_datos_curso['HP'][i]

			# print('Horas: ', hrs_practica)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['practica'][i]]
			Miercoles = profes_dispo_recortado['Miercoles']
			# print(profes_dispo_recortado)
			Miercoles_array = Miercoles.dropna().to_numpy()
			# print('Miercoles: ', Miercoles_array)

			Miercoles_corto = []

			for j in range(len(Miercoles_array)):
				Existe = Miercoles_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Miercoles_array) >= hrs_practica, hrs_practica != 0)
				if Existe == False and len(Miercoles_corto) < hrs_practica and hrs_practica != 0:
					Miercoles_corto.append(Miercoles_array[j])

			df_horario_Miercoles = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['practica'][i], 'Miercoles': Miercoles_corto})
			df_horario_final = df_horario_final.append(df_horario_Miercoles, ignore_index=True)
			df_datos_curso['HP'][i] = hrs_practica - len(Miercoles_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Martes - Practica'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe practica por curso: ', df_profes_curso['practica'][i])
			hrs_practica = df_datos_curso['HP'][i]

			# print('Horas: ', hrs_practica)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['practica'][i]]
			Martes = profes_dispo_recortado['Martes']
			# print(profes_dispo_recortado)
			Martes_array = Martes.dropna().to_numpy()
			# print('Martes: ', Martes_array)

			Martes_corto = []

			for j in range(len(Martes_array)):
				Existe = Martes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Martes_array) >= hrs_practica, hrs_practica != 0)
				if Existe == False and len(Martes_corto) < hrs_practica and hrs_practica != 0:
					Martes_corto.append(Martes_array[j])

			df_horario_Martes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['practica'][i], 'Martes': Martes_corto})
			df_horario_final = df_horario_final.append(df_horario_Martes, ignore_index=True)
			df_datos_curso['HP'][i] = hrs_practica - len(Martes_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Lunes - Practica'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe practica por curso: ', df_profes_curso['practica'][i])
			hrs_practica = df_datos_curso['HP'][i]

			# print('Horas: ', hrs_practica)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['practica'][i]]
			Lunes = profes_dispo_recortado['Lunes']
			# print(profes_dispo_recortado)
			Lunes_array = Lunes.dropna().to_numpy()
			# print('Lunes: ', Lunes_array)

			Lunes_corto = []

			for j in range(len(Lunes_array)):
				Existe = Lunes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Lunes_array) >= hrs_practica, hrs_practica != 0)
				if Existe == False and len(Lunes_corto) < hrs_practica and hrs_practica != 0:
					Lunes_corto.append(Lunes_array[j])

			df_horario_Lunes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['practica'][i], 'Lunes': Lunes_corto})
			df_horario_final = df_horario_final.append(df_horario_Lunes, ignore_index=True)
			df_datos_curso['HP'][i] = hrs_practica - len(Lunes_corto)
			# print('previa del horario final: \n', df_horario_final)

		print('Tabla del horario final - practica previa: ')
		print(df_horario_final)

		'''LABORATORIO'''
		'''Lunes - laboratorio'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe laboratorio por curso: ', df_profes_curso['laboratorio'][i])
			hrs_laboratorio = df_datos_curso['HL'][i]

			# print('Horas: ', hrs_laboratorio)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['laboratorio'][i]]
			Lunes = profes_dispo_recortado['Lunes']
			# print(profes_dispo_recortado)
			Lunes_array = Lunes.dropna().to_numpy()
			# print('Lunes: ', Lunes_array)

			Lunes_corto = []

			for j in range(len(Lunes_array)):
				Existe = Lunes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Lunes_array) >= hrs_laboratorio, hrs_laboratorio != 0)
				if Existe == False and len(Lunes_corto) < hrs_laboratorio and hrs_laboratorio != 0:
					Lunes_corto.append(Lunes_array[j])

			df_horario_Lunes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['laboratorio'][i], 'Lunes': Lunes_corto})
			df_horario_final = df_horario_final.append(df_horario_Lunes, ignore_index=True)
			df_datos_curso['HL'][i] = hrs_laboratorio - len(Lunes_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Martes - laboratorio'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe laboratorio por curso: ', df_profes_curso['laboratorio'][i])
			hrs_laboratorio = df_datos_curso['HL'][i]

			# print('Horas: ', hrs_laboratorio)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['laboratorio'][i]]
			Martes = profes_dispo_recortado['Martes']
			# print(profes_dispo_recortado)
			Martes_array = Martes.dropna().to_numpy()
			# print('Martes: ', Martes_array)

			Martes_corto = []

			for j in range(len(Martes_array)):
				Existe = Martes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Martes_array) >= hrs_laboratorio, hrs_laboratorio != 0)
				if Existe == False and len(Martes_corto) < hrs_laboratorio and hrs_laboratorio != 0:
					Martes_corto.append(Martes_array[j])

			df_horario_Martes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['laboratorio'][i], 'Martes': Martes_corto})
			df_horario_final = df_horario_final.append(df_horario_Martes, ignore_index=True)
			df_datos_curso['HL'][i] = hrs_laboratorio - len(Martes_corto)
			# print('previa del horario final: \n', df_horario_final)

		'''Miercoles - laboratorio'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe laboratorio por curso: ', df_profes_curso['laboratorio'][i])
			hrs_laboratorio = df_datos_curso['HL'][i]

			# print('Horas: ', hrs_laboratorio)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['laboratorio'][i]]
			Miercoles = profes_dispo_recortado['Miercoles']
			# print(profes_dispo_recortado)
			Miercoles_array = Miercoles.dropna().to_numpy()
			# print('Miercoles: ', Miercoles_array)

			Miercoles_corto = []

			for j in range(len(Miercoles_array)):
				Existe = Miercoles_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Miercoles_array) >= hrs_laboratorio, hrs_laboratorio != 0)
				if Existe == False and len(Miercoles_corto) < hrs_laboratorio and hrs_laboratorio != 0:
					Miercoles_corto.append(Miercoles_array[j])

			df_horario_Miercoles = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['laboratorio'][i], 'Miercoles': Miercoles_corto})
			df_horario_final = df_horario_final.append(df_horario_Miercoles, ignore_index=True)
			df_datos_curso['HL'][i] = hrs_laboratorio - len(Miercoles_corto)
			# print('previa del horario final: \n', df_horario_final)


		'''Jueves - laboratorio'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe laboratorio por curso: ', df_profes_curso['laboratorio'][i])
			hrs_laboratorio = df_datos_curso['HL'][i]

			# print('Horas: ', hrs_laboratorio)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['laboratorio'][i]]
			Jueves = profes_dispo_recortado['Jueves']
			# print(profes_dispo_recortado)
			Jueves_array = Jueves.dropna().to_numpy()
			# print('Jueves: ', Jueves_array)

			Jueves_corto = []

			for j in range(len(Jueves_array)):
				Existe = Jueves_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Jueves_array) >= hrs_laboratorio, hrs_laboratorio != 0)
				if Existe == False and len(Jueves_corto) < hrs_laboratorio and hrs_laboratorio != 0:
					Jueves_corto.append(Jueves_array[j])

			df_horario_Jueves = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['laboratorio'][i], 'Jueves': Jueves_corto})
			df_horario_final = df_horario_final.append(df_horario_Jueves, ignore_index=True)
			df_datos_curso['HL'][i] = hrs_laboratorio - len(Jueves_corto)
			# print('previa del horario final: \n', df_horario_final)


		'''Viernes - laboratorio'''

		for i in range(len(df_datos_curso['Id_curso'])):
			print('Id curso: ', df_datos_curso['Id_curso'][i])
			print('Id profe laboratorio por curso: ', df_profes_curso['laboratorio'][i])
			hrs_laboratorio = df_datos_curso['HL'][i]

			# print('Horas: ', hrs_laboratorio)
			profes_dispo_recortado = profes_dispo[profes_dispo['Id_profe'] == df_profes_curso['laboratorio'][i]]
			Viernes = profes_dispo_recortado['Viernes']
			# print(profes_dispo_recortado)
			Viernes_array = Viernes.dropna().to_numpy()
			# print('Viernes: ', Viernes_array)

			Viernes_corto = []

			for j in range(len(Viernes_array)):
				Existe = Viernes_array[j] in df_horario_final.values
				print('Resultado del segundo if', Existe == False, len(Viernes_array) >= hrs_laboratorio, hrs_laboratorio != 0)
				if Existe == False and len(Viernes_corto) < hrs_laboratorio and hrs_laboratorio != 0:
					Viernes_corto.append(Viernes_array[j])

			df_horario_Viernes = pd.DataFrame({'Curso':df_datos_curso['Id_curso'][i], 'Profesor': df_profes_curso['laboratorio'][i], 'Viernes': Viernes_corto})
			df_horario_final = df_horario_final.append(df_horario_Viernes, ignore_index=True)
			df_datos_curso['HL'][i] = hrs_laboratorio - len(Viernes_corto)
			# print('previa del horario final: \n', df_horario_final)

		print('Tabla del horario final previa: ')
		# print(df_horario_final)
		Id_horario = str(uuid.uuid4())
		df_horario_final = df_horario_final.assign(Id_horario=Id_horario)
		# print(df_horario_final)
		df_horario_final = df_horario_final.astype({'Curso':'str','Profesor':'str','Lunes':'str','Martes':'str','Miercoles':'str','Jueves':'str','Viernes':'str','Sabado':'str','Id_horario':'str'})
		df_horario_final.to_gbq('db_horario.horarios', project_id=miProyecto, if_exists='append')
		print(df_datos_curso)
		export_horario_final(Id_horario)

def export_horario_final(Id_horario):
    sql = f'''
		SELECT
            cursos.Codigo, cursos.Ciclo, cursos.Nombre as Curso, profes.Nombre as Profesor, horario.Lunes, horario.Martes, horario.Miercoles, horario.Jueves, horario.Viernes, horario.Sabado
        FROM `unmsm-horarios.db_horario.horarios` as horario
        INNER JOIN `unmsm-horarios.db_horario.cursos` as cursos ON horario.Curso = cursos.Id_curso
        INNER JOIN `unmsm-horarios.db_horario.profes` as profes ON horario.Profesor = profes.Id_profe
        WHERE horario.Id_horario= '{Id_horario}'
    '''
    df_horario_export = bq.query(sql).result().to_dataframe()
    print(df_horario_export)
    df_horario_export = df_horario_export.replace('nan',' ')
    file_name = f"./horarios/Horario_Id_{Id_horario}.xlsx"
    df_horario_export.to_excel(file_name)
    return print('Se creo un horario en un archivo excel')

@app.route('/modificarHorarios')
def modificarHorarios():
    return render_template('modificarHorarios.html')


@app.route('/modificarProfesores')
def modificarProfesores():
    return render_template('modificarProfesores.html')


if __name__ == '__main__':
    app.run(debug=True)
