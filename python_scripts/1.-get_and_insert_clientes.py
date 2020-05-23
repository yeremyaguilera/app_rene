import pandas as pd
import cleaning
import logging
import socket
import numpy as np
import datetime
import pyodbc
import pandas.io.sql as psql

HOST_NAME = socket.gethostname().lower()

# Configuramos la creación del log.
logging.basicConfig(level=logging.DEBUG,
                    filename='get_and_insert_carterafoco.log', 
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s')


import sys
sys.path.append("../")

# Configuramos la importación de los modelos de Django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reneapp.settings")

# Importamos los modelos de Django.
import django
django.setup()

from clientes.models import Cliente
from personas_beme.models import Persona

# Parámetro de la clase Cliente de la DB
nombre_columnas = [f.name for f in Cliente._meta.get_fields()]
nombre_columnas.remove('impactooperacion')
nombre_columnas.remove('cliente')
nombre_columnas.remove('operacion')


logging.info("Cargando columnas necesarias del modelo en Django \n" + str(nombre_columnas))


if HOST_NAME in ["w81-yaguile1", "vsk12-micro-neg"]:
    # Conexión con la base de datos de Riesgo
    logging.info("Cargando BD desde Query")

    sql_query = """select *
                    from Normalizacion.dbo.seguimiento_cartera_foco;"""

    logging.info("Query : \n" + sql_query)
    cnxn = pyodbc.connect(
        "Driver={SQL Server};Server=s2k_micro-rsg1" +
        ";Database=Control_Riesgo;trusted_connection=yes;")

    cursor = cnxn.cursor()
    logging.info("Conexión Lograda a SQL")
    df_clientes = psql.read_sql_query(sql_query, cnxn)
    logging.info("Lectura Lograda a SQL")
    
    relative_dir = '../excel_files/personas_beme/'
    nombre_archivo  = os.listdir(relative_dir)[0]
    df_personas = pd.read_excel(relative_dir + nombre_archivo)

elif HOST_NAME == 'yaguilera-note':
    relative_dir = '../excel_files/carterafoco/'
    nombre_archivo  = os.listdir(relative_dir)[0]

    # Archivo a importar
    df_clientes = pd.read_excel(relative_dir + nombre_archivo)
    
    relative_dir = '../excel_files/personas_beme/'
    nombre_archivo  = os.listdir(relative_dir)[0]
    df_personas = pd.read_excel(relative_dir + nombre_archivo)

    logging.info("Lectura exitosa desde .xlsx")
else:
    sys.exit()

#Limpieza de los strings de la BD
df_clientes = cleaning.normalize_df(df_clientes)
logging.info("Nomalización de datos exitosa")
df_clientes = cleaning.clean_modulo(df_clientes)
logging.info("Limpieza de datos exitosa")


df_clientes = cleaning.rename_columns_clientes(df_clientes)
df_clientes = cleaning.transform_clientes(df_clientes)
logging.info("Transformación de datos exitosa")

## INFORMACION A HARDCODEAR
## *********************************
## *********************************
## *********************************
df_clientes['ejecutivo_cartera'] = df_clientes["codigo_ejc"].apply(lambda x: cleaning.get_user_from_codigo(x, df_personas, Persona))

df_clientes['gestor']            = np.nan

# Rellenando datos que debiesen venir en las BD

df_clientes['fecha_gestion']       = datetime.datetime.now()
df_clientes['fecha_asignacion']    = datetime.datetime.now()
df_clientes['fecha_reinsistencia'] = datetime.datetime.now()
df_clientes['fecha_firma']         = datetime.datetime.now()

df_clientes['eleccion_oferta']             = np.nan
df_clientes['estado_curse']                = np.nan
df_clientes['contactabilidad']             = np.nan
df_clientes['estado']                      = np.nan
df_clientes['estado_cliente']              = np.nan
df_clientes['respuesta_cliente']           = np.nan
df_clientes['contacto_cliente_interesado'] = np.nan
df_clientes['canal_ccl']                   = np.nan
df_clientes['disponibilidad_oferta']       = False

## *********************************
## *********************************
## *********************************

# Filtrado de columnas a usar
df_clientes_filtrado = df_clientes[nombre_columnas]

df_clientes_filtrado["modulo_cli"] = df_clientes_filtrado["modulo_cli"].apply(lambda x: x.replace("_DE_LOS_RIOS", ""))
df_clientes_filtrado["modulo_cli"] = df_clientes_filtrado["modulo_cli"].apply(lambda x: x.replace("VIII_REGION_BIO_BIO_NORTE", "BIOBIO_NORTE"))
df_clientes_filtrado["modulo_cli"] = df_clientes_filtrado["modulo_cli"].apply(lambda x: x.replace("VIII_REGION_BIO_BIO_SUR", "BIOBIO_SUR"))
df_clientes_filtrado["modulo_cli"] = df_clientes_filtrado["modulo_cli"].apply(lambda x: x.replace("X_REGION_DE_LOS_LAGOS", "X_REGION"))

df_clientes_filtrado["canal_web"] = df_clientes_filtrado["canal_web"].replace(["SI", "NO"],[True, False])
df_clientes_filtrado["preaprobados_reng"] = df_clientes_filtrado["preaprobados_reng"].replace(["SI", "NO"],[True, False])

#Normalización de números de teléfono
df_clientes_filtrado['tel_cel_1']  = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_cel_1), axis = 1)
df_clientes_filtrado['tel_cel_2']  = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_cel_2), axis = 1)
df_clientes_filtrado['tel_fijo_1'] = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_fijo_1), axis = 1)
df_clientes_filtrado['tel_fijo_2'] = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_fijo_2), axis = 1)
df_clientes_filtrado['tel_fijo_1'] = df_clientes_filtrado['tel_fijo_1'].fillna(0)
df_clientes_filtrado['tel_fijo_2'] = df_clientes_filtrado['tel_fijo_2'].fillna(0)

# Reemplazando nan con None para la BD
df_clientes_filtrado_none = df_clientes_filtrado.where(pd.notnull(df_clientes_filtrado), None)

for index, cada_cliente in df_clientes_filtrado_none.iterrows():
    logging.info(index)
    if Cliente.objects.filter(cli_rut = cada_cliente.cli_rut).exists():
        logging.info("Cliente ya existe en la Base de Datos")
        logging.info(str(cada_cliente.cli_rut) + " " + str(cada_cliente.cli_nom))
    else:
        logging.info("Creación de Cliente")
        logging.info(str(cada_cliente.cli_rut) + " " + str(cada_cliente.cli_nom))
        Cliente.objects.create(**cada_cliente)


print("Proceso Finalizado con éxito!!")