import pandas as pd
import uuid

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

df_cursos = pd.read_excel('cursos.xlsx')
n_filas, n_columnas = df_cursos.shape


n_uuids = [str(uuid.uuid4()) for x in range(n_filas)]

df_cursos['Id_curso'] = n_uuids

df_cursos = df_cursos.astype({'Id_curso':'str','Ciclo':'str','Codigo':'str','Nombre':'str','HT':'int64','HP':'int64','HL':'int64'})

df_cursos = df_cursos[['Id_curso','Ciclo','Codigo','Nombre','HT','HP','HL']]

print(df_cursos)
print(df_cursos.dtypes)

# df_cursos

# file_name = f"./horarios/df_cursos.xlsx"
# df_cursos.to_excel(file_name)

# df_cursos.to_gbq(
#             'db_horario.cursos', project_id=miProyecto, if_exists='append')