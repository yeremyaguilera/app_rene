import pandas as pd
import sys
import numpy as np
import datetime

def intereses_restantes(serie):
    intereses = sum([np.ipmt(serie.ope_tasa/100, cuota, int(serie.ope_cant_cuo), -serie.ope_monto_origen_pes) for cuota in range(int(serie["ope_cuotas_pagadas"]) + 1, int(serie["ope_cant_cuo"]) + 1)])
    return np.ceil(intereses)

def saldos_insolutos(serie):
    intereses = sum([np.ppmt(serie.ope_tasa/100, cuota, int(serie.ope_cant_cuo), -serie.ope_monto_origen_pes) for cuota in range(int(serie["ope_cuotas_pagadas"]) + 1, int(serie["ope_cant_cuo"]) + 1)])
    return np.ceil(intereses)

def interes_mora(serie):
    #print(serie.dop_dia_mra-30, serie.dop_mnt_cuo, serie.ope_tasa_penal_diaria)
    if serie.dop_mnt_cuo == 0:
        interes_mra = serie.dop_dia_mra * serie.dop_sdo_tot * serie.ope_tasa_penal_diaria/100
    else:
        interes_mra = serie.dop_dia_mra * serie.dop_mnt_cuo * serie.ope_tasa_penal_diaria/100
        if serie.dop_dia_mra > 30:
            interes_mra += (serie.dop_dia_mra-30) * serie.dop_mnt_cuo * serie.ope_tasa_penal_diaria/100
            
    return int(interes_mra)

def cuota_UF(serie, valor_uf):
    if (serie.dop_mnt_cuo == 0) | (serie.dop_mnt_cuo == "NULL"):
        cuota_uf = serie.dop_sdo_tot/valor_uf
    else:
        cuota_uf = serie.dop_mnt_cuo/valor_uf
        
    return cuota_uf

def gastos_de_cobranza(serie, valor_uf):
    if serie.dop_dia_mra < 21:
        gastos = 0
    else:
        if serie.cuota_uf > 50:
            gastos = (serie.cuota_uf-50)*0.03 + 40*0.06+10*0.09
        else:
            if serie.cuota_uf > 10:
                gastos = (serie.cuota_uf-10)*0.06 + 10*0.09
            else:
                gastos = serie.cuota_uf * 0.09
    return gastos*valor_uf*serie.cuotas_atrasadas


def interes_prep(serie):
    if (serie.familia == "MF") | (serie.familia == "MRF"):
        interes_pre = serie.dop_sdo_tot * serie.ope_tasa/100
    else:
        interes_pre = 0
    return interes_pre
        
def fun_eficacia(serie):
    if (serie.eficacia_gar == 0) | (str(serie.eficacia_gar) == "nan"):
        eficacia = 0
    else:
        eficacia = 1
    return eficacia

def marc_garantia(serie):
    if serie.eficacia == 1:
        if serie.familia in ["MG", "MF", "MRF", "MRG"]:
            marca = 1
        else: 
            marca = 0
    else:
        marca = 0
    
    return marca

def antiguedad_fogape(serie):
    if serie.familia in ["MF", "MRF"]:
        antiguedad = 120 - (datetime.datetime.today().date() - serie.fec_oto).days/30
    else:
        antiguedad = 0
    return int(antiguedad)


def info_impacto(df, valor_diario_uf, periodo_de_gracia):
    valor_diario_uf = float(valor_diario_uf)
    df["prorroga_vigente"]      = np.nan
    df["max_cuo"]               = np.nan
    df["status_2"]              = np.nan
    df["extra_cuo"]             = np.nan
    df["acum_garantia"]         = np.nan

    df["ope_cuotas_por_pagar"]  = df["ope_cant_cuo"] - df["ope_cuotas_pagadas"]
    df["validez_2"]             = df["fecha_pago_final"]
    df["interes_por_recibir"]   = df.apply(lambda x: intereses_restantes(x), axis = 1)
    df["saldo_insoluto"]        = df.apply(lambda x: saldos_insolutos(x), axis = 1)
    df["interes_moratorio"]     = df.apply(lambda x: interes_mora(x), axis = 1)
    df["cuotas_atrasadas"]      = df.apply(lambda x: int(np.ceil(x.dop_dia_mra/30)), axis = 1)
    df["cuota_uf"]              = df.apply(lambda x: cuota_UF(x, valor_diario_uf), axis = 1)
    df["gastos_cobranza"]       = df.apply(lambda x: gastos_de_cobranza(x, valor_diario_uf), axis = 1)
    df["interes_prepago"]       = df.apply(lambda x: interes_prep(x), axis = 1)
    df["eficacia"]              = df.apply(lambda x: fun_eficacia(x), axis = 1)
    df["marca_garantia"]        = df.apply(lambda x: marc_garantia(x), axis = 1)
    df["antiguedad_fogape"]     = df.apply(lambda x: antiguedad_fogape(x), axis = 1)
    df["fogape"]                = df.apply(lambda x: 1 if x.antiguedad_fogape != 0 else 0, axis = 1)
    df["operacion_k"]           = df.apply(lambda x: 1 if x.marca.upper() == "K" else 0, axis = 1)

    for cada_rut in df["cli_rut"].unique():
        rut_cliente = cada_rut #cada_cliente["cli_rut"]
        operaciones_por_clientes = df[df["cli_rut"] == rut_cliente]
        acum_garantia = 0
        for index_operacion, cada_operacion in operaciones_por_clientes.iterrows():
            if cada_operacion["marca_garantia"] == 0:
                operaciones_por_clientes.loc[index_operacion, "acum_garantia"]    = 0
                df.loc[index_operacion, "acum_garantia"] = 0
            else:
                acum_garantia += cada_operacion["marca_garantia"]
                operaciones_por_clientes.loc[index_operacion, "acum_garantia"]    = acum_garantia
                df.loc[index_operacion, "acum_garantia"] = operaciones_por_clientes.loc[index_operacion, "acum_garantia"]
                
            
            operacion_prorroga = operaciones_por_clientes["fecha_pago_final"] < cada_operacion["prox_ven"]
            
            if True in list(operacion_prorroga):
                operaciones_por_clientes.loc[index_operacion, "prorroga_vigente"]    = 1
                df.loc[index_operacion, "prorroga_vigente"] = 1
                
                operaciones_por_clientes.loc[index_operacion, "max_cuo"]    = 0
                df.loc[index_operacion, "max_cuo"] = 0
                
            else:
                operaciones_por_clientes.loc[index_operacion, "prorroga_vigente"]    = 0
                df.loc[index_operacion, "prorroga_vigente"] = 0
                
                operaciones_por_clientes.loc[index_operacion, "max_cuo"]    = df.loc[index_operacion, "ope_cuotas_por_pagar"]
                df.loc[index_operacion, "max_cuo"] = df.loc[index_operacion, "ope_cuotas_por_pagar"]
                
            if len(operaciones_por_clientes) > 1:
                dataframe_without_op = operaciones_por_clientes[operaciones_por_clientes["dop_num_ope"] != operaciones_por_clientes.loc[index_operacion, "dop_num_ope"]]
                operacion_status = operaciones_por_clientes.loc[index_operacion, "prox_ven"] > dataframe_without_op["validez_2"]
                if False in list(operacion_status):
                    operaciones_por_clientes.loc[index_operacion, "status_2"]    = 0
                    df.loc[index_operacion, "status_2"] = 0

                    operaciones_por_clientes.loc[index_operacion, "extra_cuo"]    = 0
                    df.loc[index_operacion, "extra_cuo"] = 0
                else:
                    operaciones_por_clientes.loc[index_operacion, "status_2"]     = 1
                    df.loc[index_operacion, "status_2"]  = 1

                    operaciones_por_clientes.loc[index_operacion, "extra_cuo"]    = df.loc[index_operacion, "ope_cuotas_por_pagar"]
                    df.loc[index_operacion, "extra_cuo"] = df.loc[index_operacion, "ope_cuotas_por_pagar"]
            else:
                operacion_status = [operaciones_por_clientes.loc[index_operacion, "prox_ven"] > datetime.datetime.today().date()]
                operaciones_por_clientes.loc[index_operacion, "status_2"]    = 0
                df.loc[index_operacion, "status_2"] = 0
                
                operaciones_por_clientes.loc[index_operacion, "extra_cuo"]    = 0
                df.loc[index_operacion, "extra_cuo"] = 0

    return df

def string_intervalo(string):
    lista = string.split(", ")
    rango = range(int(lista[0].replace("[", "")), int(lista[1].replace("]", ""))+1)
    return rango


def consolidado_info_impacto(df_operacion_info_impacto, df_tasas_seguro, periodo_de_gracia, tasa_oferta):
    df_info_oferta = pd.DataFrame()

    ruts_unicos = df_operacion_info_impacto["cli_rut"].unique()

    for index, cada_rut in enumerate(ruts_unicos):
        df_info_oferta.loc[index, "cli_rut"]  = cada_rut
        operaciones_por_cliente = df_operacion_info_impacto[df_operacion_info_impacto["cli_rut"] == cada_rut]
        
        df_info_oferta.loc[index, "cant_ope"]       = len(operaciones_por_cliente)
        df_info_oferta.loc[index, "plazo_restante"] = max(operaciones_por_cliente["max_cuo"])+max(operaciones_por_cliente["extra_cuo"])
        
        plazo_restante = df_info_oferta.loc[index, "plazo_restante"]
        for index_tasa, each_tasa in df_tasas_seguro.iterrows():
            if int(plazo_restante) in string_intervalo(each_tasa["plazo"]):
                df_info_oferta.loc[index, "tasa_seguro"] = float(each_tasa["valor_tasa"])/100
        
        filtro_mora_cobranza = operaciones_por_cliente[operaciones_por_cliente["operacion_k"] == 0]
        
        if len(filtro_mora_cobranza) != 0:
            df_info_oferta.loc[index, "interes_moratorio"] = filtro_mora_cobranza["interes_moratorio"].sum()
            df_info_oferta.loc[index, "gastos_cobranza"]   = filtro_mora_cobranza["gastos_cobranza"].sum()
        else:
            df_info_oferta.loc[index, "interes_moratorio"] = 0
            df_info_oferta.loc[index, "gastos_cobranza"]   = 0
            
        filtro_comision = operaciones_por_cliente[(operaciones_por_cliente["operacion_k"] == 0) & (operaciones_por_cliente["marca_garantia"] == 1)]
        
        if len(filtro_comision) != 0:
            df_info_oferta.loc[index, "comision_prep"] = operaciones_por_cliente["interes_prepago"].sum()
        else:
            df_info_oferta.loc[index, "comision_prep"] = 0
        
        filtro_adeudado_sin_gar_comercial = operaciones_por_cliente[(operaciones_por_cliente["acum_garantia"] == 0) & (operaciones_por_cliente["operacion_k"] == 0)]
        saldo_sin_gar_comercial = 0
        if len(filtro_adeudado_sin_gar_comercial) != 0:
            saldo_sin_gar_comercial += filtro_adeudado_sin_gar_comercial["dop_sdo_tot"].sum()
        
        df_info_oferta.loc[index, "periodo_de_gracia"]    = periodo_de_gracia

        df_info_oferta.loc[index, "saldo_adeudado_gar"]   = operaciones_por_cliente[operaciones_por_cliente["marca_garantia"] != 0]["dop_sdo_tot"].sum()
        df_info_oferta.loc[index, "saldo_adeudado_gar_1"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 1]["dop_sdo_tot"].sum()
        df_info_oferta.loc[index, "saldo_adeudado_gar_2"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 2]["dop_sdo_tot"].sum()
        df_info_oferta.loc[index, "saldo_adeudado_gar_3"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 3]["dop_sdo_tot"].sum()
        df_info_oferta.loc[index, "saldo_adeudado_gar_4"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 4]["dop_sdo_tot"].sum()
        
        df_info_oferta.loc[index, "saldo_adeudado_gar_final"]   = df_info_oferta.loc[index, "saldo_adeudado_gar"]*(1+tasa_oferta)**df_info_oferta.loc[index, "periodo_de_gracia"]
        df_info_oferta.loc[index, "saldo_adeudado_gar_1_final"] = df_info_oferta.loc[index, "saldo_adeudado_gar_1"]*(1+tasa_oferta)**df_info_oferta.loc[index, "periodo_de_gracia"]
        df_info_oferta.loc[index, "saldo_adeudado_gar_2_final"] = df_info_oferta.loc[index, "saldo_adeudado_gar_2"]*(1+tasa_oferta)**df_info_oferta.loc[index, "periodo_de_gracia"]
        df_info_oferta.loc[index, "saldo_adeudado_gar_3_final"] = df_info_oferta.loc[index, "saldo_adeudado_gar_3"]*(1+tasa_oferta)**df_info_oferta.loc[index, "periodo_de_gracia"]
        df_info_oferta.loc[index, "saldo_adeudado_gar_4_final"] = df_info_oferta.loc[index, "saldo_adeudado_gar_4"]*(1+tasa_oferta)**df_info_oferta.loc[index, "periodo_de_gracia"]

        
        
        df_info_oferta.loc[index, "saldo_sin_gar_comercial"] = (saldo_sin_gar_comercial + \
                                                                df_info_oferta.loc[index, "comision_prep"] + \
                                                                df_info_oferta.loc[index, "gastos_cobranza"] + \
                                                                df_info_oferta.loc[index, "interes_moratorio"])*(1+ df_info_oferta.loc[index, "tasa_seguro"]) + \
                                                                df_info_oferta.loc[index, "saldo_adeudado_gar"]*df_info_oferta.loc[index, "tasa_seguro"]
        
        
        df_info_oferta.loc[index, "saldo_sin_gar_comercial_final"] = df_info_oferta.loc[index, "saldo_sin_gar_comercial"]*(1+0.99/100)**df_info_oferta.loc[index, "periodo_de_gracia"]
        
        filtro_adeudado_consumo = operaciones_por_cliente[(operaciones_por_cliente["acum_garantia"] == 0) & (operaciones_por_cliente["operacion_k"] == 1)]
        df_info_oferta.loc[index, "saldo_adeudado_consumo"] = (filtro_adeudado_consumo["dop_sdo_tot"].sum()+filtro_adeudado_consumo["interes_moratorio"].sum()+filtro_adeudado_consumo["gastos_cobranza"].sum())*(1+df_info_oferta.loc[index, "tasa_seguro"])
        df_info_oferta.loc[index, "saldo_adeudado_consumo_final"] = df_info_oferta.loc[index, "saldo_adeudado_consumo"]*(1+0.99/100)**df_info_oferta.loc[index, "periodo_de_gracia"]
        
        if df_info_oferta.loc[index, "saldo_adeudado_consumo_final"] != 0:
            df_info_oferta.loc[index, "num_cuotas_max_k"] = 48 - periodo_de_gracia
        else:
            df_info_oferta.loc[index, "num_cuotas_max_k"] = 0

        if df_info_oferta.loc[index, "saldo_adeudado_gar_1_final"] != 0:
            if operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 1]["antiguedad_fogape"].values - periodo_de_gracia < 0:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_1"] = 0
            else:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_1"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 1]["antiguedad_fogape"].values - periodo_de_gracia
        else:
            df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_1"] = 0

        if df_info_oferta.loc[index, "saldo_adeudado_gar_2_final"] != 0:
            if operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 2]["antiguedad_fogape"].values - periodo_de_gracia < 0:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_2"] = 0
            else:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_2"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 2]["antiguedad_fogape"].values - periodo_de_gracia
        else:
            df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_2"] = 0

        if df_info_oferta.loc[index, "saldo_adeudado_gar_3_final"] != 0:
            if operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 3]["antiguedad_fogape"].values - periodo_de_gracia < 0:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_3"] = 0
            else:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_3"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 3]["antiguedad_fogape"].values - periodo_de_gracia
        else:
            df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_3"] = 0

        if df_info_oferta.loc[index, "saldo_adeudado_gar_4_final"] != 0:
            if operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 4]["antiguedad_fogape"].values - periodo_de_gracia < 0:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_4"] = 0
            else:
                df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_4"] = operaciones_por_cliente[operaciones_por_cliente["acum_garantia"] == 4]["antiguedad_fogape"].values - periodo_de_gracia
        else:
            df_info_oferta.loc[index, "num_cuotas_max_fogape_gar_4"] = 0

        #print(operaciones_por_cliente["perfil_de_riesgo"], operaciones_por_cliente["perfil_de_riesgo"].unique())
        df_info_oferta.loc[index, "perfil_riesgo"] = operaciones_por_cliente["perfil_de_riesgo"].unique()[0]
        
        filtro_pago_mensual = operaciones_por_cliente[operaciones_por_cliente["prorroga_vigente"] == 0]
        df_info_oferta.loc[index, "pago_mensual"] = filtro_pago_mensual["dop_mnt_cuo"].sum()
        
        df_info_oferta.loc[index, "ope_tasa_media"] = filtro_pago_mensual["ope_tasa"].mean()
        
        total_a_pagar = 0
        for index_ope, cada_operacion in operaciones_por_cliente.iterrows():
            total_a_pagar += cada_operacion["ope_cuotas_por_pagar"]*int(cada_operacion["dop_mnt_cuo"])
            total_a_pagar += cada_operacion["interes_moratorio"]  + cada_operacion["gastos_cobranza"]
        
        df_info_oferta.loc[index, "total_a_pagar_hoy"] = total_a_pagar
    
    return df_info_oferta

def crea_oferta(df_consolidado_info_impacto, periodo_de_gracia, tasa_oferta):

    df_oferta = pd.DataFrame()

    for index, cada_cliente in df_consolidado_info_impacto.iterrows():
        df_oferta.loc[index, "cli_rut"] = int(cada_cliente["cli_rut"])
        df_oferta.loc[index, "ope_tasa"] = tasa_oferta
        df_oferta.loc[index, "ope_tasa_oferta_1"] = tasa_oferta
        df_oferta.loc[index, "ope_tasa_oferta_2"] = tasa_oferta

        monto_temp_o1 = np.ceil(cada_cliente["pago_mensual"]*(1-0.05))
        monto_temp_o2 = np.ceil(cada_cliente["pago_mensual"]*(1-0.3))

        monto_final_credito = cada_cliente["saldo_adeudado_gar_final"]+cada_cliente["saldo_sin_gar_comercial_final"]+cada_cliente["saldo_adeudado_consumo_final"]

        num_cuotas_oferta_1 = np.ceil(np.nper(df_oferta.loc[index, "ope_tasa"], -monto_temp_o1, monto_final_credito))
        num_cuotas_oferta_2 = np.ceil(np.nper(df_oferta.loc[index, "ope_tasa"], -monto_temp_o2, monto_final_credito))

        if num_cuotas_oferta_1 > 84 - periodo_de_gracia:
            num_cuotas_oferta_1 = 84 - periodo_de_gracia

        if num_cuotas_oferta_2 > 84 - periodo_de_gracia:
            num_cuotas_oferta_2 = 84 - periodo_de_gracia

            
        ## OFERTA 1
        df_oferta.loc[index, "num_cuotas_oferta_1"] = num_cuotas_oferta_1
        df_oferta.loc[index, "monto_oferta_1"]      = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_oferta_1, -monto_final_credito))

        ##MONTO CUOTA COMERCIAL
        df_oferta.loc[index, "monto_c_oferta_1"]     = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_oferta_1, -cada_cliente["saldo_sin_gar_comercial_final"]))
        
        
        ##NUMERO DE CUOTAS CONSUMO
        if cada_cliente["num_cuotas_max_k"] == 0:
            num_cuotas_k_1 = num_cuotas_oferta_1
        else:
            if cada_cliente["num_cuotas_max_k"] < num_cuotas_oferta_1:
                num_cuotas_k_1 = cada_cliente["num_cuotas_max_k"].values
            else:
                num_cuotas_k_1 = num_cuotas_oferta_1
        ##MONTO CUOTA CONSUMO
        df_oferta.loc[index, "monto_k_oferta_1"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_k_1, -cada_cliente["saldo_adeudado_consumo_final"]))
        df_oferta.loc[index, "num_cuotas_k_1"]   = num_cuotas_k_1
        
        
        ##NUMERO DE CUOTAS SI GAR 1 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_1"] == 0:
            num_cuotas_gar_1_oferta_1 = num_cuotas_oferta_1
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_1"] < num_cuotas_oferta_1:
                num_cuotas_gar_1_oferta_1 = cada_cliente["num_cuotas_max_fogape_gar_1"].values
            else:
                num_cuotas_gar_1_oferta_1 = num_cuotas_oferta_1
        ##MONTO CUOTA GAR 1 SI FOGAPE
        df_oferta.loc[index, "monto_gar_1_oferta_1"]     = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_1_oferta_1, -cada_cliente["saldo_adeudado_gar_1_final"]))
        df_oferta.loc[index, "num_cuotas_gar_1_oferta_1"] = num_cuotas_gar_1_oferta_1
        
        
        ##NUMERO DE CUOTAS SI GAR 2 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_2"] == 0:
            num_cuotas_gar_2_oferta_1 = num_cuotas_oferta_1
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_2"] < num_cuotas_oferta_1:
                num_cuotas_gar_2_oferta_1 = cada_cliente["num_cuotas_max_fogape_gar_2"].values
            else:
                num_cuotas_gar_2_oferta_1 = num_cuotas_oferta_1
        ##MONTO CUOTA GAR 2 SI FOGAPE
        df_oferta.loc[index, "monto_gar_2_oferta_1"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_2_oferta_1, -cada_cliente["saldo_adeudado_gar_2_final"]))
        df_oferta.loc[index, "num_cuotas_gar_2_oferta_1"] = num_cuotas_gar_2_oferta_1
        
        
        ##NUMERO DE CUOTAS SI GAR 3 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_3"] == 0:
            num_cuotas_gar_3_oferta_1 = num_cuotas_oferta_1
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_3"] < num_cuotas_oferta_1:
                num_cuotas_gar_3_oferta_1 = cada_cliente["num_cuotas_max_fogape_gar_3"].values
            else:
                num_cuotas_gar_3_oferta_1 = num_cuotas_oferta_1
        ##MONTO CUOTA GAR 3 SI FOGAPE
        df_oferta.loc[index, "monto_gar_3_oferta_1"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_3_oferta_1, -cada_cliente["saldo_adeudado_gar_3_final"]))
        df_oferta.loc[index, "num_cuotas_gar_3_oferta_1"] = num_cuotas_gar_3_oferta_1
        
        
        ##NUMERO DE CUOTAS SI GAR 4 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_4"] == 0:
            num_cuotas_gar_4_oferta_1 = num_cuotas_oferta_1
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_4"] < num_cuotas_oferta_1:
                num_cuotas_gar_4_oferta_1 = cada_cliente["num_cuotas_max_fogape_gar_4"].values
            else:
                num_cuotas_gar_4_oferta_1 = num_cuotas_oferta_1
        ##MONTO CUOTA GAR 4 SI FOGAPE
        df_oferta.loc[index, "monto_gar_4_oferta_1"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_4_oferta_1, -cada_cliente["saldo_adeudado_gar_4_final"]))
        df_oferta.loc[index, "num_cuotas_gar_4_oferta_1"] = num_cuotas_gar_4_oferta_1

        df_oferta.loc[index, "monto_oferta_1"] = df_oferta.loc[index, "monto_c_oferta_1"] + df_oferta.loc[index, "monto_k_oferta_1"] + df_oferta.loc[index, "monto_gar_1_oferta_1"] + df_oferta.loc[index, "monto_gar_2_oferta_1"] + df_oferta.loc[index, "monto_gar_3_oferta_1"] + df_oferta.loc[index, "monto_gar_4_oferta_1"]
        df_oferta.loc[index, "per_rebaja_oferta_1"]    = (1-df_oferta.loc[index, "monto_oferta_1"]/cada_cliente["pago_mensual"])
        df_oferta.loc[index, "total_a_pagar_oferta_1"] = df_oferta.loc[index, "num_cuotas_oferta_1"] * df_oferta.loc[index, "monto_oferta_1"]


        
        ##OFERTA 2
        
        
        df_oferta.loc[index, "num_cuotas_oferta_2"] = num_cuotas_oferta_2
        df_oferta.loc[index, "monto_oferta_2"]      = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_oferta_2, -monto_final_credito))

        ##MONTO CUOTA COMERCIAL
        df_oferta.loc[index, "monto_c_oferta_2"]     = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_oferta_2, -cada_cliente["saldo_sin_gar_comercial_final"]))
        
        
        ##NUMERO DE CUOTAS CONSUMO
        if cada_cliente["num_cuotas_max_k"] == 0:
            num_cuotas_k_2 = num_cuotas_oferta_2
        else:
            if cada_cliente["num_cuotas_max_k"] < num_cuotas_oferta_2:
                num_cuotas_k_2 = cada_cliente["num_cuotas_max_k"].values
            else:
                num_cuotas_k_2 = num_cuotas_oferta_2
        ##MONTO CUOTA CONSUMO
        df_oferta.loc[index, "monto_k_oferta_2"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_k_2, -cada_cliente["saldo_adeudado_consumo_final"]))
        df_oferta.loc[index, "num_cuotas_k_2"]   = num_cuotas_k_2
        
        
        ##NUMERO DE CUOTAS SI GAR 1 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_1"] == 0:
            num_cuotas_gar_1_oferta_2 = num_cuotas_oferta_2
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_1"] < num_cuotas_oferta_2:
                num_cuotas_gar_1_oferta_2 = cada_cliente["num_cuotas_max_fogape_gar_1"].values
            else:
                num_cuotas_gar_1_oferta_2 = num_cuotas_oferta_2
        ##MONTO CUOTA GAR 1 SI FOGAPE
        df_oferta.loc[index, "monto_gar_1_oferta_2"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_1_oferta_2, -cada_cliente["saldo_adeudado_gar_1_final"]))
        df_oferta.loc[index, "num_cuotas_gar_1_oferta_2"]   = num_cuotas_gar_1_oferta_2
        
        
        ##NUMERO DE CUOTAS SI GAR 2 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_2"] == 0:
            num_cuotas_gar_2_oferta_2 = num_cuotas_oferta_2
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_2"] < num_cuotas_oferta_2:
                num_cuotas_gar_2_oferta_2 = cada_cliente["num_cuotas_max_fogape_gar_2"].values
            else:
                num_cuotas_gar_2_oferta_2 = num_cuotas_oferta_2
        ##MONTO CUOTA GAR 2 SI FOGAPE
        df_oferta.loc[index, "monto_gar_2_oferta_2"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_2_oferta_2, -cada_cliente["saldo_adeudado_gar_2_final"]))
        df_oferta.loc[index, "num_cuotas_gar_2_oferta_2"]   = num_cuotas_gar_2_oferta_2
        
        
        ##NUMERO DE CUOTAS SI GAR 3 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_3"] == 0:
            num_cuotas_gar_3_oferta_2 = num_cuotas_oferta_2
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_3"] < num_cuotas_oferta_2:
                num_cuotas_gar_3_oferta_2 = cada_cliente["num_cuotas_max_fogape_gar_3"].values
            else:
                num_cuotas_gar_3_oferta_2 = num_cuotas_oferta_2
        ##MONTO CUOTA GAR 3 SI FOGAPE
        df_oferta.loc[index, "monto_gar_3_oferta_2"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_3_oferta_2, -cada_cliente["saldo_adeudado_gar_3_final"]))
        df_oferta.loc[index, "num_cuotas_gar_3_oferta_2"]   = num_cuotas_gar_3_oferta_2
        
        
        ##NUMERO DE CUOTAS SI GAR 4 FOGAPE
        if cada_cliente["num_cuotas_max_fogape_gar_4"] == 0:
            num_cuotas_gar_4_oferta_2 = num_cuotas_oferta_2
        else:
            if cada_cliente["num_cuotas_max_fogape_gar_4"] < num_cuotas_oferta_2:
                num_cuotas_gar_4_oferta_2 = cada_cliente["num_cuotas_max_fogape_gar_4"].values
            else:
                num_cuotas_gar_4_oferta_2 = num_cuotas_oferta_2
        ##MONTO CUOTA GAR 4 SI FOGAPE
        df_oferta.loc[index, "monto_gar_4_oferta_2"] = np.ceil(np.pmt(df_oferta.loc[index, "ope_tasa"], num_cuotas_gar_4_oferta_2, -cada_cliente["saldo_adeudado_gar_4_final"]))
        df_oferta.loc[index, "num_cuotas_gar_4_oferta_2"]   = num_cuotas_gar_4_oferta_2

        df_oferta.loc[index, "monto_oferta_2"] = df_oferta.loc[index, "monto_c_oferta_2"] + df_oferta.loc[index, "monto_k_oferta_2"] + df_oferta.loc[index, "monto_gar_1_oferta_2"] + df_oferta.loc[index, "monto_gar_2_oferta_2"] + df_oferta.loc[index, "monto_gar_3_oferta_2"] + df_oferta.loc[index, "monto_gar_4_oferta_2"]
        df_oferta.loc[index, "per_rebaja_oferta_2"]    = (1-df_oferta.loc[index, "monto_oferta_2"]/cada_cliente["pago_mensual"])
        df_oferta.loc[index, "total_a_pagar_oferta_2"] = df_oferta.loc[index, "num_cuotas_oferta_2"] * df_oferta.loc[index, "monto_oferta_2"]

    df_oferta.drop("ope_tasa", axis = 1, inplace = True)
    return df_oferta