import pandas as pd
import logging
import datetime

# Configuramos la creación del log.
logging.basicConfig(level=logging.DEBUG,
                    filename='get_and_insert_impacto.log', 
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
from clientes.models import Cliente
from info_complementaria.models import TasaSeguro, UF, PeriodoGracia, TasaOferta

#Carga de Operaciones de la BD
df_operaciones  = pd.DataFrame(list(Operacion.objects.all().values()))
logging.info("Se Cargaron las Operaciones de la Base de Datos")
df_operaciones.rename(columns = {"cliente_id": "cli_rut"}, inplace = True)


#Carga de Tasas Seguro de la BD
df_tasas_seguro  = pd.DataFrame(list(TasaSeguro.objects.all().values()))
logging.info("Se Cargaron las Tasas de Seguro de la Base de Datos")

#Carga del valor de la UF del día de hoy
valor_diario_uf = UF.objects.get(dia = datetime.datetime.today()).valor_uf
logging.info("Se Cargó el valor de la UF de la Base de Datos")

#Carga del periodo de gracia y la tasa oferta de la BD
periodo_de_gracia = PeriodoGracia.objects.all().reverse()[0].periodo_de_gracia
logging.info("Se Cargó el Periodo de Graciasor de la Base de Datos")
tasa_oferta       = TasaOferta.objects.all().reverse()[0].ope_tasa/100
logging.info("Se Cargó la tasa de Oferta de la Base de Datos")

df_operaciones_info_impacto = genera_oferta.info_impacto(df_operaciones, valor_diario_uf, periodo_de_gracia)
logging.info("Se Calculó el impacto de cada operación")

df_consolidado_info_impacto = genera_oferta.consolidado_info_impacto(df_operaciones_info_impacto, df_tasas_seguro, periodo_de_gracia, tasa_oferta)
logging.info("Se Consolidó el impacto de las operación")

#Parámetros para insertar en la BD el Impacto de las operaciones
nombre_columnas = [f.name for f in ImpactoOperacion._meta.get_fields()][1:]

# Fecha de ingreso de impactos (Depende de la UF y días de mora)
df_consolidado_info_impacto['fecha_de_impacto'] = datetime.datetime.today().date()

#Agreagamos el objecto Cliente
df_consolidado_info_impacto['cliente'] = [Cliente.objects.get(cli_rut = x) for x in df_consolidado_info_impacto['cli_rut']]
df_consolidado_info_impacto = df_consolidado_info_impacto[nombre_columnas]

df_consolidado_info_impacto = df_consolidado_info_impacto.where(pd.notnull(df_consolidado_info_impacto), None)


for index, cada_impacto in df_consolidado_info_impacto.iterrows():
    logging.info(index)
    if ImpactoOperacion.objects.filter(cliente__cli_rut = cada_impacto.cliente.cli_rut).exists():
        logging.info("Cliente ya tiene impacto en la Base de Datos")
        logging.info(cada_impacto.cliente)
    else:
        logging.info("Creación de Cliente")
        logging.info(cada_impacto.cliente)
        ImpactoOperacion.objects.create(**cada_impacto)

print("Proceso Finalizado con éxito!!")