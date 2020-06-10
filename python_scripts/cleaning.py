import pandas as pd
import numpy as np
import datetime

def crea_rangos(dataframe):
    tipo_var = []
    rango    = []
    cant_de_elementos = []
    
    for cada_columna in dataframe:
        tipo_var.append(dataframe.dtypes[cada_columna])
        if dataframe.dtypes[cada_columna] in ["int64", "float64", "datetime64[ns]"]:
            if len(dataframe[cada_columna].unique()) > 15:
                rango.append([dataframe[cada_columna].min(), dataframe[cada_columna].max()])
            else:
                rango.append(list(dataframe[cada_columna].unique()))
        else:
            rango.append(list(dataframe[cada_columna].unique()))
            
        cant_de_elementos.append(len(dataframe[cada_columna].unique()))
        
    df_rango = pd.DataFrame({"Variable": dataframe.columns, "Tipo": tipo_var, "Cantidad de Elementos": cant_de_elementos, "Rango": rango})
    
    return df_rango


def quita_espacio_a_textos(texto):
    lista = texto.split(" ")
    while '' in lista:
        lista.remove('')
    separator = ' '
    return separator.join(lista)


def limpia_espacios(dataframe):
    df_temp = dataframe.copy()
    for cada_columna in df_temp:
        if df_temp.dtypes[cada_columna] == "object":
            df_temp[cada_columna] = df_temp[cada_columna].apply(lambda x: str(x))
            
            df_temp[cada_columna] = df_temp[cada_columna].apply(lambda x: quita_espacio_a_textos(x))
        df_temp[cada_columna] = df_temp[cada_columna].apply(lambda x: np.nan if str(x) in ['nan', 'SIN INFO'] else x)
    return df_temp

def normalize_df(df):
    
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace("á", "a")
    df.columns = df.columns.str.replace("é", "e")
    df.columns = df.columns.str.replace("í", "i")
    df.columns = df.columns.str.replace("ó", "o")
    df.columns = df.columns.str.replace("ú", "u")
    df.columns = df.columns.str.replace("ñ", "n")

    df = limpia_espacios(df)
    
    return df

def clean_modulo(df):
    df["modulo"] = df["modulo"].apply(lambda x: x.upper().replace(" ", "_"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("Ó", "O"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("Í", "I"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("METROP.", "METROPOLITANA"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("_-_LOS_RIOS", ""))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("_-_LOS_LAGOS", ""))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("_-_LOS_LAGOS", ""))

    ## RESPETAR ORDEN DE EJECUCION
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("QUINTA_COSTA", "V_REGION_COSTA"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("QUINTA_CORDILLERA", "V_REGION_CORDILLERA"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("SEXTO", "VI_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("SEPTIMO", "VII_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("OCTAVA_CORDILLERA", "VIII_REGION_CORDILLERA"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("NOVENA_SUR", "IX_REGION_SUR"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("NOVENA_NORTE", "IX_REGION_NORTE"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("DECIMO_PRIMERO", "XI_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("DECIMO_SEGUNDO", "XII_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("DECIMO_CUARTO", "XIV_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("DECIMO", "X_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("PRIMER", "I_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("SEGUNDO", "II_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("TERCERO", "III_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("CUARTO", "IV_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("QUINCEAVO", "XV_REGION"))

    
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("REGION_METROPOLITANA", "METROPOLITANA"))
    return df

def rename_columns_clientes(df):
    df.rename(columns={"rut": "cli_rut"}, inplace = True)
    df.rename(columns={"nombre_cliente": "cli_nom"}, inplace = True)
    df.rename(columns={"impacto_en_gasto_pe_inicial": "impacto_gasto_pe_inicial"}, inplace = True)
    df.rename(columns={"impacto_en_gasto_pe_hoy": "impacto_gasto_pe_hoy"}, inplace = True)
    df.rename(columns={"telefono_particular": "tel_fijo_1"}, inplace = True)
    df.rename(columns={"telefono_comercial": "tel_fijo_2"}, inplace = True)
    df.rename(columns={"telefono_celular1": "tel_cel_1"}, inplace = True)
    df.rename(columns={"telefono_celular2": "tel_cel_2"}, inplace = True)
    df.rename(columns={"direc_particular": "direccion_particular"}, inplace = True)
    df.rename(columns={"direc_comer": "direccion_comercial"}, inplace = True)
    df.rename(columns={"estado_de_morosidad_hoy": "estado_diario"}, inplace = True)
    df.rename(columns={"zona": "zona_cli"}, inplace = True)
    df.rename(columns={"modulo": "modulo_cli"}, inplace = True)
    df.rename(columns={"nombre_oficna": "sucursal_cli"}, inplace = True)
    df.rename(columns={"tiene_postergacion_cargada_hoy": "postergacion_cargada_hoy"}, inplace = True)
    df.rename(columns={"tiene_reneg_web_disponible": "renegociacion_web_disponible"}, inplace = True)
    df.rename(columns={"esta_en_simulador_de_riesgo": "oferta_simulador_riesgo"}, inplace = True)
    df.rename(columns={"campana_poster_preferencial": "campana_postergacion_preferencial"}, inplace = True)
    df.rename(columns={"esta_inscrito_en_formulario_web": "inscrito_formulario_web"}, inplace = True)
    df.rename(columns={"posee_reneg_preaprobada": "renegociacion_preaprobada"}, inplace = True)
    df.rename(columns={"maximo_dias_de_mora_com-con_hoy": "maximo_dias_mora"}, inplace = True)
    df.rename(columns={"saldo_moroso_com-con_hoy": "saldo_moroso_hoy"}, inplace = True)
    df.rename(columns={"fecha_actualizacion": "fecha_actualizacion_datos"}, inplace = True)
    df.rename(columns={"ult_gest": "fecha_registro"}, inplace = True)
    df.rename(columns={"gestiones": "n_gestiones"}, inplace = True)
    df.rename(columns={"gestiones_efectivas": "n_gestiones_efectivas"}, inplace = True)

    return df

def normalize_formulario(serie):
    serie = serie.str.replace(" - ", "_")
    serie = serie.str.replace(" ", "_")
    serie = serie.str.replace("á", "a")
    serie = serie.str.replace("é", "e")
    serie = serie.str.replace("í", "i")
    serie = serie.str.replace("ó", "o")
    serie = serie.str.replace("ú", "u")
    serie = serie.str.upper()
    serie = serie.str.strip()

    return serie

def string_to_date(string):
    print(string)
    "El formato debe ser YYYmmdd"
    if str(string) == 'nan':
        date = None
    else:
        date = datetime.datetime.strptime(str(int(string)), '%Y%m%d').date()
    return date


def transform_clientes(df):
    df["zona_cli"]      = df["zona_cli"].apply(lambda x: x.replace(" ", "_"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.replace(" ", "_"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.replace("á", "a"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.replace("é", "e"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.replace("í", "i"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.replace("ó", "o"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.replace("ú", "u"))
    df["estado_diario"] = df["estado_diario"].apply(lambda x: x.upper())
    df['fecha_actualizacion_datos']   = [datetime.datetime.strptime(str(x), '%Y%m%d').date() for x in df['fecha_actualizacion_datos']]
    df['fecha_asignacion_foco']       = [datetime.datetime.strptime(str(x), '%Y%m%d').date() for x in df['fecha_asignacion_foco']]
    df['maximo_dias_mora'].fillna(0, inplace = True)
    df['impacto_gasto_pe_hoy'].fillna(0, inplace = True)
    df['saldo_moroso_hoy'].fillna(0, inplace = True)
    
    return df

def limpia_telefono(string):
    if (str(string) != "nan") and (len(string) == len("[056] [009] [0045150550] [00000]")):
        string_temp = string.split("] [")
        codigo_pais = string_temp[0].replace("[0", "")
        codigo_movil = string_temp[1].replace("00", "")
        numero_movil = string_temp[2][-8:]
        return int(codigo_pais+codigo_movil+numero_movil)
    else:
        return 0

def transform_operaciones(df):
    df["fecha_curse"]          = df.apply(lambda x: x.fec_oto if str(x.fecha_curse) == 'NaT' else x.fecha_curse, axis = 1)
    df["primer_ven"]           = df.apply(lambda x: x.prox_ven if str(x.primer_ven) == 'NaT' else x.primer_ven, axis = 1)
    df["fecha_pago_final"]     = df.apply(lambda x: x["prox_ven"] if str(x["fecha_pago_final"]) in ['NaT', 'None'] else x["fecha_pago_final"], axis = 1)
    df["fecha_curse"]          = df.apply(lambda x: x.fec_oto if str(x.fecha_curse) in ['NaT', 'None'] else x.fecha_curse, axis = 1)
    df["primer_ven"]           = df.apply(lambda x: x.prox_ven if str(x.primer_ven) in ['NaT', 'None'] else x.primer_ven, axis = 1)
    df["eficacia_gar"]         = df["eficacia_gar"].replace(np.nan, 0)
    df["ope_valor_tasa_penal"] = df["ope_valor_tasa_penal"].replace(np.nan, df["ope_valor_tasa_penal"].max())
    df["ope_tasa_penal_diaria"] = df["ope_valor_tasa_penal"]/365
    df["cpd"]                  = df['dec_cpd']
    df["dop_num_ope"]          = df.apply(lambda x: int(x.dop_num_ope) if str(x.dop_num_ope).isdigit() else x.dop_num_ope, axis = 1)
    if 'perfil_riesgo' in df.columns:
        df["perfil_de_riesgo"] = df["perfil_riesgo"].str.strip()

    df["perfil_de_riesgo"].replace(np.nan, "BUENO", inplace = True)
    df["madurezpe"].replace(np.nan, 0, inplace = True)
    df["ope_cuotas_pagadas"].replace(np.nan, 0, inplace = True)
    df["ope_num_mes_cuo"].replace(np.nan, 1, inplace = True)
    df["dop_mnt_cuo"]      = df.apply(lambda x: x["dop_sdo_tot"]/x["ope_cant_cuo"] if ((str(x["dop_mnt_cuo"]) == "nan") | (x["dop_mnt_cuo"] == 0)) & (x["ope_cant_cuo"] != 0) else x["dop_mnt_cuo"], axis = 1)

    return df

def clean_zona_turnos(serie_zona):
    serie_zona.replace("NORTE", "ZONA_NORTE", inplace = True)
    serie_zona.replace("CENTRO", "ZONA_CENTRO", inplace = True)
    serie_zona.replace("SUR", "ZONA_SUR", inplace = True)
    return serie_zona

def clean_modulo_turnos(df):
    df["modulo"] = df["modulo"].str.upper()
    df["modulo"] = df["modulo"].str.replace(" ", "_")
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("Ó", "O"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("Í", "I"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("METROP.", "METROPOLITANA"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("VIII_REGION_BIO_BIO_NORTE", "BIOBIO_NORTE"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("VIII_REGION_BIO_BIO_SUR", "BIOBIO_SUR"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("X_REGION_DE_LOS_LAGOS", "X_REGION"))
    df["modulo"] = df["modulo"].apply(lambda x: x.replace("XIV_REGION_DE_LOS_RIOS", "XIV_REGION"))
    return df

def clean_sucursal_turnos(df):
    df["sucursal"] = df["sucursal"].str.replace("á", "a")
    df["sucursal"] = df["sucursal"].str.replace("é", "e")
    df["sucursal"] = df["sucursal"].str.replace("í", "i")
    df["sucursal"] = df["sucursal"].str.replace("ó", "o")
    df["sucursal"] = df["sucursal"].str.replace("ú", "u")
    df["sucursal"] = df["sucursal"].str.upper()
    df["sucursal"] = df["sucursal"].str.replace(" ", "_")
    df["sucursal"] = df["sucursal"].str.replace("(", "")
    df["sucursal"] = df["sucursal"].str.replace(")", "")
    df["sucursal"] = df["sucursal"].str.replace("_SERVIESTADO", "")
    return df

def clean_trabaja_hoy(df):
    df["trabaja_hoy"] = df["trabaja_hoy"].str.upper()
    df["trabaja_hoy"] = df["trabaja_hoy"].str.replace("SI", "DISPONIBLE")
    df["trabaja_hoy"] = df["trabaja_hoy"].str.replace("NO", "NO_DISPONIBLE")
    return df

def get_user_from_codigo(codigo, df_personas):
    email_persona = df_personas[df_personas['COD EC'] == codigo]["Mail"].values
    if len(email_persona) == 1:
        user = email_persona[0].split("@")[0].lower()
    else:
        user = ""
    return user