import pandas as pd
import cleaning
import logging


# Configuramos la creación del log.
logging.basicConfig(level=logging.DEBUG,
                    filename='get_and_insert_personas_beme.log', 
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

from personas_beme.models import Persona


# Ingresamos la ruta del archivo con la información de las personas de BEME.
ruta_archivo = "../excel_files/personas_beme/Personas_BEME.xlsx"
# Leemos el archivo.
df_personas = pd.read_excel(ruta_archivo)

# Mensaje a log.
logging.info("Archivo " + ruta_archivo + " leído....")

# Limpiamos y normalizamos los datos.
df_personas = cleaning.normalize_df(df_personas)
df_personas = cleaning.clean_modulo(df_personas)

# Botamos los rut de las personas.
df_personas.drop("rut", axis = 1, inplace = True)

# Cambiamos los nombres de las columnas para adaptarlas a nuestro modelo en Django.
df_personas.rename(columns = {"materno": "apellido_materno"}, inplace = True)
df_personas.rename(columns = {"mail"   : "email"}, inplace = True)

# Le damos formato a los datos de las columnas.
df_personas["zona"]                = df_personas["zona"].apply(lambda x: x.upper().replace(" ", "_"))
df_personas["email"]               = df_personas["email"].str.lower()
df_personas["nombre"]              = df_personas["nombre"].str.title()
df_personas["apellido"]            = df_personas["apellido"].str.title()
df_personas["apellido_materno"]    = df_personas["apellido_materno"].str.title()

# Editamos los valores de cargo, para filtrar.
df_personas["cargo"]               = df_personas.apply(lambda x: ("_").join(x.cargo.split(" ")[:2]), axis = 1)

# Creamos el codigo_personas_beme con el usuario del email.
df_personas["codigo_persona_beme"] = df_personas.apply(lambda x: str(x.email).split("@")[0], axis = 1)
logging.info("Archivo limpiado y normalizado....")

df_personas["cargo"] = df_personas["cargo"].apply(lambda x: x.upper().replace("AUTONOMO", "COMERCIAL"))
cargos = ['ASESOR_COMERCIAL', 'EJECUTIVO_COMERCIAL', 'ASISTENTE_COMERCIAL']

df_personas = df_personas[df_personas["cargo"].isin(cargos)]
logging.info("Archivo fitrado por : " + str(cargos))

logging.info("Valores nullos botados: ")
logging.info(str((df_personas.isna().sum())))

df_personas.dropna(inplace = True)
df_personas.drop('cod_ec',axis = 1, inplace = True)
df_personas = df_personas.drop_duplicates(subset='email', keep='first')

for index, cada_persona_beme in df_personas.iterrows():
    logging.info(index)
    if Persona.objects.filter(codigo_persona_beme = cada_persona_beme.codigo_persona_beme).exists():
        logging.info("Persona ya existe en la Base de Datos")
        logging.info(str(cada_persona_beme.codigo_persona_beme) + " " + str(cada_persona_beme.nombre))
        continue
    else:
        logging.info("Creación de persona_beme")
        logging.info(str(cada_persona_beme.codigo_persona_beme) + " " + str(cada_persona_beme.nombre))
        Persona.objects.create(**cada_persona_beme)


print("Proceso Finalizado con éxito!!")