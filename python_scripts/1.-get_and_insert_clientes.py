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

from reneapp.settings import BASE_DIR
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
                    from Normalizacion.dbo.seguimiento_cartera_foco
                    where Zona = 'ZONA CENTRO'
                    and Modulo = 'Metrop. Centro';"""

    logging.info("Query : \n" + sql_query)
    cnxn = pyodbc.connect(
        "Driver={SQL Server};Server=s2k_micro-rsg1" +
        ";Database=Control_Riesgo;trusted_connection=yes;")

    cursor = cnxn.cursor()
    logging.info("Conexión Lograda a SQL")
    df_clientes = psql.read_sql_query(sql_query, cnxn)
    logging.info("Lectura Lograda a SQL")
    
    relative_dir = os.path.join(BASE_DIR, 'excel_files', 'personas_beme')
    nombre_archivo  = os.listdir(relative_dir)[0]
    df_personas = pd.read_excel(os.path.join(relative_dir , nombre_archivo))

elif HOST_NAME == 'yaguilera-note':
    relative_dir = os.path.join(BASE_DIR, 'excel_files', 'carterafoco')
    nombre_archivo  = os.listdir(relative_dir)[0]

    # Archivo a importar
    df_clientes = pd.read_excel(os.path.join(relative_dir , nombre_archivo))
    
    relative_dir = os.path.join(BASE_DIR, 'excel_files', 'personas_beme')
    nombre_archivo  = os.listdir(relative_dir)[0]

    df_personas = pd.read_excel(os.path.join(relative_dir , nombre_archivo))

    logging.info("Lectura exitosa desde .xlsx")
else:
    sys.exit()

#Limpieza de los strings de la BD
df_clientes = cleaning.normalize_df(df_clientes)
logging.info("Nomalización de datos exitosa")
df_clientes = cleaning.clean_modulo(df_clientes)
logging.info("Limpieza de datos exitosa")


print(df_clientes.columns)
df_clientes = cleaning.rename_columns_clientes(df_clientes)
df_clientes = cleaning.transform_clientes(df_clientes)
logging.info("Transformación de datos exitosa")

## INFORMACION A HARDCODEAR
## *********************************
## *********************************
## *********************************
df_clientes['ejecutivo_cartera'] = df_clientes["codigo_ejc"].apply(lambda x: cleaning.get_user_from_codigo(x, df_personas))
df_clientes['ejecutivo_cartera'] = df_clientes["ejecutivo_cartera"].apply(lambda x: Persona.objects.get(codigo_persona_beme = x) if Persona.objects.filter(codigo_persona_beme = x).exists() else np.nan)

df_clientes['gestor']            = df_clientes["usuario_gestor"].apply(lambda x: Persona.objects.get(codigo_persona_beme = x) if Persona.objects.filter(codigo_persona_beme = x).exists() else np.nan)

df_clientes['contactabilidad']      = cleaning.normalize_formulario(df_clientes['contactabilidad'])
df_clientes['respuesta_cliente']    = cleaning.normalize_formulario(df_clientes['respuesta_cliente'])
df_clientes['estado_negociacion']   = cleaning.normalize_formulario(df_clientes['estado_negociacion'])
df_clientes['estado_negociacion']   = [None if x=="NONE" else x for x in df_clientes['estado_negociacion']]


nombre_columnas.remove("email")
nombre_columnas.remove("observacion")
# Rellenando datos que debiesen venir en las BD

df_clientes['fecha_asignacion_gestor']  = datetime.datetime.now().date()
df_clientes['fecha_registro']           = [cleaning.string_to_date(x) for x in df_clientes['fecha_registro']]
df_clientes['fecha_regula']             = [cleaning.string_to_date(x) for x in df_clientes['fecha_regula']]
df_clientes['max_otorgamiento']         = [cleaning.string_to_date(x) for x in df_clientes['max_otorgamiento']]

#df_clientes['email']        = np.nan
#df_clientes['observacion']  = np.nan

## *********************************
## *********************************
## *********************************

# Filtrado de columnas a usar
#[print(x) for x in nombre_columnas]
#[print(x) for x in df_clientes.columns]
df_clientes_filtrado = df_clientes[nombre_columnas]

df_clientes_filtrado["modulo_cli"].replace("_DE_LOS_RIOS", "", inplace=True)
df_clientes_filtrado["modulo_cli"].replace("VIII_REGION_BIO_BIO_NORTE", "BIOBIO_NORTE", inplace=True)
df_clientes_filtrado["modulo_cli"].replace("VIII_REGION_BIO_BIO_SUR", "BIOBIO_SUR", inplace=True)
df_clientes_filtrado["modulo_cli"].replace("X_REGION_DE_LOS_LAGOS", "X_REGION", inplace=True)

#Normalización de números de teléfono
df_clientes_filtrado['tel_cel_1']  = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_cel_1), axis = 1)
df_clientes_filtrado['tel_cel_2']  = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_cel_2), axis = 1)
df_clientes_filtrado['tel_fijo_1'] = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_fijo_1), axis = 1)
df_clientes_filtrado['tel_fijo_2'] = df_clientes_filtrado.apply(lambda x: cleaning.limpia_telefono(x.tel_fijo_2), axis = 1)
df_clientes_filtrado['tel_fijo_1'].fillna(0, inplace = True)
df_clientes_filtrado['tel_fijo_2'].fillna(0, inplace = True)

# Reemplazando nan con None para la BD
df_clientes_filtrado["max_proc"] = df_clientes_filtrado["max_proc"].astype(object)

df_clientes_filtrado_none = df_clientes_filtrado.where(pd.notnull(df_clientes_filtrado), None)

for index, cada_cliente in df_clientes_filtrado_none.iterrows():
    logging.info(index)
    print(cada_cliente.cli_rut, cada_cliente.cli_nom)
    cliente, created = Cliente.objects.update_or_create(cli_rut = cada_cliente.cli_rut, defaults=cada_cliente.to_dict())
    if not created:
        logging.info("Cliente ya existe en la Base de Datos")
        logging.info(str(cada_cliente.cli_rut) + " " + str(cada_cliente.cli_nom))
    else:
        logging.info("Creación de Cliente")
        logging.info(str(cada_cliente.cli_rut) + " " + str(cada_cliente.cli_nom))

print("Proceso Finalizado con éxito!!")