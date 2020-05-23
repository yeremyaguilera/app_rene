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
                    filename='get_and_insert_operaciones.log', 
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

from operaciones.models import Operacion
from clientes.models import Cliente

# Parámetro de la clase Operacion de la DB
nombre_columnas = [f.name for f in Operacion._meta.get_fields()]

logging.info("Cargando columnas necesarias del modelo en Django \n" + str(nombre_columnas))

if HOST_NAME in ["w81-yaguile1", "vsk12-micro-neg"]:
    # Conexión con la base de datos de Riesgo
    logging.info("Cargando BD desde Query")

    sql_query = """select *
                    from normalizacion.[dbo].Base_operaciones_cliente_simulador
                    where cli_rut in ( select cli_rut
                                        from normalizacion.[dbo].Base_clientes_simulador_Mensual_red_sucursal
                                        where Gestiona_red_of=1)
                    and Nodo_ope_final like 'RENEGOCIACIÓN <60';
                    """

    logging.info("Query : \n" + sql_query)
    cnxn = pyodbc.connect(
        "Driver={SQL Server};Server=s2k_micro-rsg1" +
        ";Database=Control_Riesgo;trusted_connection=yes;")

    cursor = cnxn.cursor()
    logging.info("Conexión Lograda a SQL")
    df_operaciones = psql.read_sql_query(sql_query, cnxn)
    logging.info("Lectura Lograda a SQL")

elif HOST_NAME == 'yaguilera-note':
    relative_dir = '../excel_files/initial_db/'
    nombre_archivo  = os.listdir(relative_dir)[0]

    # Archivo a importar
    df_operaciones = pd.read_excel(relative_dir + nombre_archivo, sheet_name="Base2")

    logging.info("Lectura exitosa desde .xlsx")
else:
    sys.exit()

# Limpieza de datos de las operaciones
df_operaciones = cleaning.normalize_df(df_operaciones)
logging.info("Nomalización de datos exitosa")
df_operaciones = cleaning.transform_operaciones(df_operaciones)
logging.info("Transformación de datos exitosa")

# Filtro con los clientes que tiene la base de datos.
df_operaciones.dropna(subset=['cli_rut'], inplace = True)
df_operaciones = df_operaciones.reset_index(drop = True)

ruts = df_operaciones["cli_rut"].unique()

for cada_rut in ruts:
    if Cliente.objects.filter(cli_rut = cada_rut).exists():
        cliente = Cliente.objects.get(cli_rut = cada_rut)
        cliente.disponibilidad_oferta = True
        cliente.save()
    else:
        df_operaciones = df_operaciones[df_operaciones["cli_rut"] != cada_rut].reset_index(drop = True)

logging.info("Se Marcaron con oferta los clientes que tienen operaciones")

# En vez del rut de la persona, va el objecto cliente de la BD
df_operaciones["cliente"] = [Cliente.objects.get(cli_rut = x) for x in df_operaciones["cli_rut"]]

# Filtro de columnas de la BD
df_operaciones = df_operaciones[nombre_columnas]


for index, cada_operacion in df_operaciones.iterrows():
    logging.info(index)
    if Operacion.objects.filter(dop_num_ope = cada_operacion.dop_num_ope).exists():
        logging.info("Operación ya existe en la Base de Datos")
        logging.info(str(cada_operacion.cliente) + " " + str(cada_operacion.dop_num_ope))
    else:
        logging.info("Creación de Operación")
        logging.info(str(cada_operacion.cliente) + " " + str(cada_operacion.dop_num_ope))
        Operacion.objects.create(**cada_operacion)


print("Proceso Finalizado con éxito!!")