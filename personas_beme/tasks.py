
from celery.decorators import task
from celery import shared_task, Celery
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.forms.models import model_to_dict


import datetime
today_srt = datetime.datetime.today().date().strftime("%d-%m-%Y")

from .models import Persona
from clientes.models import Cliente
from operaciones.models import Operacion, ImpactoOperacion
from django.db.models import Q

import os
import time
import numpy as np
import pandas as pd
import pythoncom

import string
import xlwings
import pyodbc
import pandas.io.sql as psql
logger = get_task_logger(__name__)


from django.conf import settings
from reneapp.settings import BASE_DIR, BROKER_URL

@task(name="mul")
def mul(x, y):
    return x*y


@task()
def creador_excel_gestion_task(cada_persona_beme, clientes_dict, operaciones_dict, atributos_cliente, atributos_operacion):
    
    path_a_excel_base = os.path.join(BASE_DIR, 'python_scripts', "Simulador Repro BASE.xlsm")
    pythoncom.CoInitialize()
    relative_dir = os.path.join(BASE_DIR, 'excel_files', 'gestiones_a_realizar')    
    wb               = xlwings.Book(path_a_excel_base)
    hoja_clientes    = wb.sheets["Base"]
    hoja_operaciones = wb.sheets["Base2"]
    
    operaciones = pd.DataFrame.from_dict(operaciones_dict)
    operaciones.sort_values(by=["cliente_id"], inplace = True)
    operaciones.reset_index(drop = True, inplace = True)
    print(operaciones)
    operaciones['fec_oto']          = [datetime.datetime.strptime(str(x).split("T")[0], '%Y-%m-%d') for x in operaciones['fec_oto']]
    operaciones['fecha_curse']      = [datetime.datetime.strptime(str(x).split("T")[0], '%Y-%m-%d') for x in operaciones['fecha_curse']]
    operaciones['fecha_pago_final'] = [datetime.datetime.strptime(str(x).split("T")[0], '%Y-%m-%d') for x in operaciones['fecha_pago_final']]
    operaciones['primer_ven']       = [datetime.datetime.strptime(str(x).split("T")[0], '%Y-%m-%d') for x in operaciones['primer_ven']]
    operaciones['prox_ven']         = [datetime.datetime.strptime(str(x).split("T")[0], '%Y-%m-%d') for x in operaciones['prox_ven']]


    clientes    = pd.DataFrame.from_dict(clientes_dict)      
    clientes.rename(columns = {'ejecutivo_cartera_id': 'ejecutivo_cartera'}, inplace = True)
    clientes.replace([True, False], ["SI", "NO"], inplace = True)
    #Para cada columna
    for cada_columna in range(29):
        cada_letra = get_letter(cada_columna)
                
        #Si la columna tiene el nombre dentro de los atributos del modelo
        if hoja_clientes.range(cada_letra + str(1)).value in atributos_cliente:
            #Escribe en el excel
            columna_excel = cada_letra
            #Iteramos sobre los clientes, las filas
            for num_fila, cada_cliente in clientes.iterrows():
                fila_excel = int(num_fila)+2
                fila_excel = str(fila_excel)
                if hoja_clientes.range(cada_letra + str(1)).value == "ejecutivo_cartera":
                    hoja_clientes.range(columna_excel + fila_excel).value = cada_cliente.loc["nombre_ejecutivo_cartera"]
                else:
                    hoja_clientes.range(columna_excel + fila_excel).value = cada_cliente.loc[hoja_clientes.range(cada_letra + str(1)).value]
       
    for cada_columna in range(35):
        if hoja_operaciones.range(get_letter(cada_columna) + str(1)).value in atributos_operacion:
            columna_excel = get_letter(cada_columna)
            #Iteramos sobre las operaciones, las filas
            n_cuota = 1
            n_clave = 1
            for num_fila_operaciones in range(len(operaciones)):
                #print(num_fila_operaciones,cada_operacion["cliente_id"], cada_operacion["dop_num_ope"] )
                operaciones_del_cliente = operaciones[operaciones['cliente_id'] == operaciones.loc[num_fila_operaciones, "cliente_id"]]
                cant_ope = len(operaciones_del_cliente)
                        
                fila_excel = str(int(num_fila_operaciones)+2)
                if hoja_operaciones.range(columna_excel + str(1)).value == "cli_rut":
                    hoja_operaciones.range(columna_excel + fila_excel).value = operaciones.loc[num_fila_operaciones, "cliente_id"]
                            
                elif hoja_operaciones.range(columna_excel + str(1)).value == "dec_cpd":
                    hoja_operaciones.range(columna_excel + fila_excel).value = operaciones.loc[num_fila_operaciones, "cpd"]
                        
                elif hoja_operaciones.range(columna_excel + str(1)).value == "cant_cuo":
                    hoja_operaciones.range(columna_excel + fila_excel).value = cant_ope
                         
                elif hoja_operaciones.range(columna_excel + str(1)).value == "n_cuota":
                    hoja_operaciones.range(columna_excel + fila_excel).value = n_cuota
                    n_cuota+=1    
                elif hoja_operaciones.range(columna_excel + str(1)).value == "clave":
                    hoja_operaciones.range(columna_excel + fila_excel).value = str(operaciones.loc[num_fila_operaciones, "cliente_id"]) + " - " + str(n_clave) + "1"
                    n_clave+=1
                            
                elif hoja_operaciones.range(columna_excel + str(1)).value == "num_ope":
                    hoja_operaciones.range(columna_excel + fila_excel).value = operaciones.loc[num_fila_operaciones, "dop_num_ope"]
                            
                elif hoja_operaciones.range(columna_excel + str(1)).value == "dop_sdo_cst":
                    hoja_operaciones.range(columna_excel + fila_excel).value = 0
                            
                elif hoja_operaciones.range(columna_excel + str(1)).value == "ope_num_mes_cuo":
                    hoja_operaciones.range(columna_excel + fila_excel).value = 1
                            
                elif hoja_operaciones.range(columna_excel + str(1)).value == "ope_tasa_penal":
                    hoja_operaciones.range(columna_excel + fila_excel).value = operaciones.loc[num_fila_operaciones, "ope_tasa_penal_diaria"]*365
                else:
                    hoja_operaciones.range(columna_excel + fila_excel).value = operaciones.loc[num_fila_operaciones, hoja_operaciones.range(columna_excel + str(1)).value]
            
                if n_cuota-1 == cant_ope:
                    n_cuota = 1
                if n_clave-1 == cant_ope:
                    n_clave = 1 
    folder_name = os.path.join(relative_dir, cada_persona_beme['zona'], cada_persona_beme['modulo'], today_srt)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_name   = cada_persona_beme['codigo_persona_beme'] + "_" + cada_persona_beme['nombre'] +  "_" + cada_persona_beme['apellido'] + "_gestion.xlsm"
    wb.save(os.path.join(folder_name, file_name))

    wb.close()
    return None

def get_letter(num):
    resto = num%len(string.ascii_uppercase)
    ciclo = num//len(string.ascii_uppercase)
    
    if ciclo == 0:
        primera = ""
    else:
        primera = string.ascii_uppercase[ciclo-1]
    
    segunda = string.ascii_uppercase[resto]
    
    return primera+segunda