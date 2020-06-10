import pandas as pd
import numpy as np
import logging
import datetime

# Configuramos la creación del log.
logging.basicConfig(level=logging.DEBUG,
                    filename='get_and_insert_oferta.log', 
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

import sys
sys.path.append("../")

import cleaning, genera_oferta


# Configuramos la importación de los modelos de Django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reneapp.settings")

# Importamos los modelos de Django.
import django
django.setup()

from operaciones.models import Operacion, ImpactoOperacion
from clientes.models import OfertaCliente, Cliente
from info_complementaria.models import PeriodoGracia, TasaOferta


df_consolidado_info_impacto = pd.DataFrame(list(ImpactoOperacion.objects.all().values()))

df_consolidado_info_impacto.rename(columns = {"cliente_id": "cli_rut"}, inplace = True)

logging.info("Se Cargaron los Impactos de Operaciones de la Base de Datos")


#Carga del periodo de gracia y la tasa oferta de la BD
periodo_de_gracia = PeriodoGracia.objects.all().reverse()[0].periodo_de_gracia
logging.info("Se Cargó el Periodo de Graciasor de la Base de Datos")
tasa_oferta       = TasaOferta.objects.all().reverse()[0].ope_tasa/100
logging.info("Se Cargó la tasa de Oferta de la Base de Datos")

df_oferta = genera_oferta.crea_oferta(df_consolidado_info_impacto, periodo_de_gracia, tasa_oferta)
logging.info("Se generó la Oferta")

df_oferta['fecha_de_oferta'] = datetime.datetime.today()
df_oferta['cliente']         = [Cliente.objects.get(cli_rut = x) for x in df_oferta['cli_rut']]
nombre_columnas              = [f.name for f in OfertaCliente._meta.get_fields()][1:]
df_oferta                    = df_oferta[nombre_columnas]

df_oferta.replace([-np.inf, np.nan], [np.nan, np.nan], inplace = True)
df_oferta = df_oferta.where(pd.notnull(df_oferta), 0)

RUT_SIN_OFERTA = []
for index, cada_oferta in df_oferta.iterrows():
    if cada_oferta.isna().sum().sum() != 0:
        RUT_SIN_OFERTA.append(int(cada_oferta.cliente.cli_rut))

logging.info("Se tienen los siguientes RUTs con problemas para generar oferta \n" + str(RUT_SIN_OFERTA))

# Reemplazando nan con None para la BD
df_oferta.replace([-np.inf, np.nan], [np.nan, np.nan], inplace = True)
df_oferta = df_oferta.where(pd.notnull(df_oferta), 0)

for index, cada_oferta in df_oferta.iterrows():
    logging.info(index)
    if OfertaCliente.objects.filter(cliente__cli_rut = cada_oferta.cliente.cli_rut).exists():
        logging.info("Cliente ya tiene Oferta en la Base de Datos")
        logging.info(cada_oferta.cliente)
    else:
        logging.info("Creación de Oferta")
        logging.info(cada_oferta.cliente)
        OfertaCliente.objects.create(**cada_oferta)

print("Proceso Finalizado con éxito!!")