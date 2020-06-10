from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from reneapp.settings import BASE_DIR
from .models import EjecutivoComercial, Persona, AsistenteComercial
from gestion.models import Contraparte
from clientes.models import Cliente, OfertaCliente
from operaciones.models import Operacion, ImpactoOperacion
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.forms.models import model_to_dict

import datetime
today_srt = datetime.datetime.today().date().strftime("%d-%m-%Y")

from django.db.models import Q
from django.db.models import Sum

from .forms import FormularioClienteDB, FormularioClienteExcel, EmailForm, UploadFileForm, PersonaForm, ContraparteForm
import pyodbc
import os
import string
import xlwings
import pandas as pd
import pandas.io.sql as psql
import socket
import pythoncom
import numpy as np

from django.core.paginator import Paginator
from personas_beme import tasks
from python_scripts import cleaning

HOST_NAME = socket.gethostname().lower()
# Create your views here.
def get_all_fields_from_form(instance):
    """"
    Return names of all available fields from given Form instance.

    :arg instance: Form instance
    :returns list of field names
    :rtype: list
    """
    fields = list(instance().base_fields)

    for field in list(instance().declared_fields):
        if field not in fields:
            fields.append(field)
    return fields

def permisos_de_grupo(user):
    permisos = []
    if user.groups.filter(name='Asesores').exists():
        permisos.append('Asesores')
    if user.groups.filter(name='Asistentes').exists():
        permisos.append('Asistentes')
    if user.groups.filter(name='Ejecutivos').exists():
        permisos.append('Ejecutivos')
    return permisos

def email_sender(ejecutivo, contraparte, cliente):

    email_ejecutivo  = ejecutivo.email
    nombre_ejecutivo = ejecutivo.__str__()

    email_contraparte  = contraparte.email
    nombre_contraparte = contraparte.__str__()

    nombre_cliente = cliente.cli_nom
    rut_cliente    = cliente.cli_rut
    respuesta_elegida = cliente.respuesta_cliente

    if email_contraparte == "":
        email_contraparte = 'yaguile1@microempresas.bancoestado.cl'

    # Query a EXECutar
    cmd_prod_executesp = """ EXEC msdb.dbo.sp_send_dbmail
        @profile_name = 'Correoht',
        @recipients = '{}',
        @subject = 'Oferta Aceptada',
        @body = '<!doctype html>
                <html lang="en">
                    <head>
                        <!-- Required meta tags -->
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

                        <!-- Bootstrap CSS -->
                    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                    </head>
                        <body>
                            <div> {}!, El cliente {} ha aceptado la {} de Renegociación : <a href = "http://{}:8002/info_clientes/?q={}" >Ver Detalle</a> </div>
                            <div> La gestión fue realizada por {}.</div>
                            <div> Contacto: {}</div>
                            <br />
                            <div> Saludos, </div>
                            <div> Equipo APP RENE </div>
                            <br />
                        </body>
                </html>',
        @body_format = 'HTML' ;""".format(email_contraparte, nombre_contraparte, nombre_cliente, respuesta_elegida, HOST_NAME, rut_cliente, nombre_ejecutivo, email_ejecutivo)

    if HOST_NAME in ["w81-yaguile1", "vsk12-micro-neg"]:
        # Conexión con la base de datos de Riesgo
        cnxn = pyodbc.connect(driver              = "{SQL Server}",
                             server                = "s2k_micro-rsg1",
                             database              = "msdb",
                             UID                   = "gest",
                             PWD                   = "gestion",
                             trusted_connection    = "no")

        # # Creación del cursor para hacer la query
        cursor = cnxn.cursor()
        
        # Commit para executar
        cnxn.autocommit = True

        # Execución de la query
        cursor.execute(cmd_prod_executesp)

        # Cierre de la conexión
        cnxn.close()
    return "Envío de email a {}".format(email_contraparte)

def create_table_a_gestionar(persona_instance):
    zona = persona_instance.zona
    modulo = persona_instance.modulo
    relative_dir = os.path.join(BASE_DIR, 'excel_files', 'gestiones_a_realizar', zona, modulo)
    if not os.path.exists(relative_dir):
        fechas = []
    else:
        fechas  = os.listdir(relative_dir)
    df_table = pd.DataFrame(columns={"fecha", "usuario", "gestor", "file_name"})

    for cada_fecha in fechas:
        dir_fechas = os.path.join(relative_dir, cada_fecha)
        nombre_archivos = os.listdir(dir_fechas)
        for cada_archivo in nombre_archivos:
            if Persona.objects.filter(codigo_persona_beme = cada_archivo.split("_")[0]).exists:
                fila = {"fecha"     : cada_fecha, 
                        "usuario"   : cada_archivo.split("_")[0],
                        "gestor"    : Persona.objects.get(codigo_persona_beme = cada_archivo.split("_")[0]),
                        "file_name" : os.path.join('excel_files', 'gestiones_a_realizar', zona, modulo, cada_fecha, cada_archivo)}
            else:
                fila = {"fecha"     : None, 
                        "usuario"   : None,
                        "gestor"    : None,
                        "file_name" : None}
            df_table = df_table.append(fila, ignore_index = True)

    return df_table

def create_table_consolidacion(persona_instance):
    zona = persona_instance.zona
    modulo = persona_instance.modulo
    personas_a_consolidar = Persona.objects.filter(Q(zona = zona) & Q(modulo = modulo) & ~Q(cargo = "ASESOR_COMERCIAL")).order_by('cargo', 'nombre')

    list_personas_a_consolidar              = []
    list_n_clientes_asignados               = []
    list_impacto_total                      = []
    list_n_clientes_asignados_con_oferta_simulador    = []
    list_n_clientes_morosos                 = []
    list_n_morosos_contactados              = []
    list_impacto_morosos                    = []
    list_perc_avance                        = []

    for cada_persona_a_consolidar in personas_a_consolidar:
        clientes = Cliente.objects.filter(gestor = cada_persona_a_consolidar)
        n_clientes_asignados = clientes.count()
        impacto_total = Cliente.objects.filter(gestor = cada_persona_a_consolidar).aggregate(Sum('impacto_gasto_pe_hoy'))['impacto_gasto_pe_hoy__sum']
        if impacto_total == None:
            impacto_total = 0
            
        n_clientes_asignados_con_oferta_simulador = clientes.filter(oferta_simulador_riesgo = "SI").count()
        n_clientes_morosos              = clientes.filter(estado_diario = "MOROSO").count()
        impacto_morosos                 = clientes.filter(estado_diario = "MOROSO").aggregate(Sum('impacto_gasto_pe_hoy'))['impacto_gasto_pe_hoy__sum']
        n_morosos_contactados           = clientes.filter(estado_diario = "MOROSO", contactabilidad = "CONTACTO_TITULAR_OK").count()

        if impacto_morosos == None:
            impacto_morosos = 0
        
        list_personas_a_consolidar.append(cada_persona_a_consolidar)
        list_n_clientes_asignados.append(n_clientes_asignados)
        list_impacto_total.append(impacto_total)
        list_n_clientes_asignados_con_oferta_simulador.append(n_clientes_asignados_con_oferta_simulador)
        list_n_clientes_morosos.append(n_clientes_morosos)
        list_impacto_morosos.append(impacto_morosos)
        list_n_morosos_contactados.append(n_morosos_contactados)

        if n_clientes_asignados != 0:
            list_perc_avance.append((n_clientes_asignados-n_clientes_morosos)/n_clientes_asignados)
        else:
            list_perc_avance.append(0)
    #print(list_personas_a_consolidar, list_n_clientes_asignados, list_impacto_total, list_n_clientes_asignados_con_oferta_simulador, list_n_clientes_morosos, list_impacto_morosos, list_perc_avance, list_n_morosos_contactados)    
    return  list_personas_a_consolidar, list_n_clientes_asignados, list_impacto_total, list_n_clientes_asignados_con_oferta_simulador, list_n_clientes_morosos, list_impacto_morosos, list_perc_avance, list_n_morosos_contactados

def create_stats_asignador(persona_instance, clientes):
    clientes_sin_gestor = clientes.filter(gestor = None).count()
    total_clientes      = clientes.count()

    n_asistentes_no_disponibles = AsistenteComercial.objects.filter(modulo = persona_instance.modulo, 
                                                                    zona = persona_instance.zona, 
                                                                    status = "NO_DISPONIBLE").count()

    asistentes_disponibles      = AsistenteComercial.objects.filter(modulo = persona_instance.modulo, 
                                                                    zona = persona_instance.zona, 
                                                                    status = "DISPONIBLE")
    
    asistentes_disponibles_con_carga = 0
    n_clientes_por_asistente = []
    for cada_asistente_disponible in asistentes_disponibles:
        n_clientes_por_asistente.append(Cliente.objects.filter(gestor = cada_asistente_disponible).count())
        if Cliente.objects.filter(gestor = cada_asistente_disponible).exists():
            asistentes_disponibles_con_carga += 1
    
    n_asistentes_disponibles                    = asistentes_disponibles.count()
    personas_asignadas_a_asistentes_disponibles = Cliente.objects.filter(gestor__in=list(asistentes_disponibles)).count()
    carga_promedio_asistentes_disponibles       = round(personas_asignadas_a_asistentes_disponibles/asistentes_disponibles.count(), 2)

    n_ejecutivos_no_disponibles = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo, 
                                                                    zona = persona_instance.zona, 
                                                                    status = "NO_DISPONIBLE").count()
                                                                    
    ejecutivos_disponibles      = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo, 
                                                                    zona = persona_instance.zona, 
                                                                    status = "DISPONIBLE")
    
    ejecutivos_disponibles_con_carga = 0
    n_clientes_por_ejecutivo = []
    for cada_ejecutivos_disponibles in ejecutivos_disponibles:
        n_clientes_por_ejecutivo.append(Cliente.objects.filter(gestor = cada_ejecutivos_disponibles).count())
        if Cliente.objects.filter(gestor = cada_ejecutivos_disponibles).exists():
            ejecutivos_disponibles_con_carga += 1

    n_ejecutivos_disponibles                    = ejecutivos_disponibles.count()
    personas_asignadas_a_ejecutivos_disponibles = Cliente.objects.filter(gestor__in=list(ejecutivos_disponibles)).count()
    carga_promedio_ejecutivos_disponibles       = round(personas_asignadas_a_ejecutivos_disponibles/ejecutivos_disponibles.count(), 2)

    stats = {'total_clientes'                           : total_clientes, 
            'clientes_sin_gestor'                       : clientes_sin_gestor,
            'n_ejecutivos_no_disponibles'               : n_ejecutivos_no_disponibles,
            'n_ejecutivos_disponibles'                  : n_ejecutivos_disponibles,
            'ejecutivos_disponibles_con_carga'          : ejecutivos_disponibles_con_carga,
            'carga_promedio_ejecutivos_disponibles'     : carga_promedio_ejecutivos_disponibles,
            'carga_std_ejecutivos'                      : round(np.std(n_clientes_por_ejecutivo), 2),
            'carga_minima_ejecutivos'                   : np.min(n_clientes_por_ejecutivo),
            'carga_maxima_ejecutivos'                   : np.max(n_clientes_por_ejecutivo),
            'n_asistentes_no_disponibles'               : n_asistentes_no_disponibles,
            'n_asistentes_disponibles'                  : n_asistentes_disponibles,
            'asistentes_disponibles_con_carga'          : asistentes_disponibles_con_carga,
            'carga_promedio_asistentes_disponibles'     : carga_promedio_asistentes_disponibles,
            'carga_std_asistentes'                      : round(np.std(n_clientes_por_asistente), 2),
            'carga_minima_asistentes'                   : np.min(n_clientes_por_asistente),
            'carga_maxima_asistentes'                   : np.max(n_clientes_por_asistente)}

    return stats

@staff_member_required
def asignador_de_cartera(request):
    user_instance      = User.objects.get(username=request.user.username)
    persona_instance   = Persona.objects.get(codigo_persona_beme = user_instance.username)
    persona_form       = PersonaForm(persona = persona_instance)
    permisos           = permisos_de_grupo(user_instance)

    if request.POST:
        ## VACIAR GESTION ASIGNADA
        if "asignacion_0" in request.POST:
            clientes = Cliente.objects.filter(modulo_cli = persona_instance.modulo,
                                                zona_cli = persona_instance.zona).exclude(gestor = None).only('gestor')
            for cada_cliente in clientes:
                cada_cliente.gestor = None
                #cada_cliente.fecha_asignacion_gestor = datetime.datetime.now().date()
                cada_cliente.save()

            #Cliente.objects.bulk_update(clientes, ['gestor', 'fecha_asignacion_gestor'])

        elif "asignacion_1" in request.POST:
            clientes = Cliente.objects.filter(modulo_cli = persona_instance.modulo,
                                                zona_cli = persona_instance.zona,
                                                ejecutivo_cartera__status = "DISPONIBLE")
            for cada_cliente in clientes:
                cada_cliente.gestor = cada_cliente.ejecutivo_cartera

            Cliente.objects.bulk_update(clientes, ['gestor'])

        elif "asignacion_2" in request.POST:
            ejecutivos_no_disponible    = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "NO_DISPONIBLE").values("codigo_persona_beme", 
                                                                                                            'codigo_sucursal')
            ejecutivos_ya_asignados = []
            for cada_ejecutivo_no_disponible in ejecutivos_no_disponible:
                ejecutivos_disponible   = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "DISPONIBLE",
                                                                            codigo_sucursal = cada_ejecutivo_no_disponible['codigo_sucursal']).exclude(codigo_persona_beme__in = ejecutivos_ya_asignados).first()
                if ejecutivos_disponible != None:
                    clientes = Cliente.objects.filter(ejecutivo_cartera__codigo_persona_beme = cada_ejecutivo_no_disponible['codigo_persona_beme'])
                    for cada_cliente in clientes:
                        cada_cliente.gestor = ejecutivos_disponible

                    Cliente.objects.bulk_update(clientes, ['gestor'])
                    ejecutivos_ya_asignados.append(ejecutivos_disponible.codigo_persona_beme)
        
        elif "asignacion_3" in request.POST:
            ejecutivos_no_disponible    = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "NO_DISPONIBLE").values("codigo_persona_beme", 
                                                                                                            'codigo_sucursal')
            
            for cada_ejecutivo_no_disponible in ejecutivos_no_disponible:
                ejecutivo_disponible   = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "DISPONIBLE",
                                                                            codigo_sucursal = cada_ejecutivo_no_disponible['codigo_sucursal']).first()
                if ejecutivo_disponible != None:
                    clientes = Cliente.objects.filter(ejecutivo_cartera__codigo_persona_beme = cada_ejecutivo_no_disponible['codigo_persona_beme'])
                    for cada_cliente in clientes:
                        cada_cliente.gestor = ejecutivo_disponible

                    Cliente.objects.bulk_update(clientes, ['gestor'])

        elif "asignacion_4" in request.POST:
            ejecutivos_no_disponible    = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "NO_DISPONIBLE").values("codigo_persona_beme", 
                                                                                                            'codigo_sucursal')
            
            for cada_ejecutivo_no_disponible in ejecutivos_no_disponible:
                ejecutivos_disponibles_en_sucursal   = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                                        zona = persona_instance.zona,
                                                                                        status = "DISPONIBLE",
                                                                                        codigo_sucursal = cada_ejecutivo_no_disponible['codigo_sucursal'])
                
                n_ejecutivos_disponibles_en_sucursal  = ejecutivos_disponibles_en_sucursal.count()
                
                if n_ejecutivos_disponibles_en_sucursal != 0:
                    clientes    = Cliente.objects.filter(ejecutivo_cartera__codigo_persona_beme = cada_ejecutivo_no_disponible['codigo_persona_beme']).values_list("cli_rut", flat = True)
                    n_clientes  = len(clientes)
                    paginator   = Paginator(clientes, np.ceil(n_clientes/n_ejecutivos_disponibles_en_sucursal))
                        
                    for page_number, ejecutivo_disponible in enumerate(ejecutivos_disponibles_en_sucursal, 1):
                        current_page        = paginator.get_page(page_number)
                        current_cli_ruts    = current_page.object_list
                        clientes_por_pagina = Cliente.objects.filter(cli_rut__in=current_cli_ruts)
                        for cada_cliente_en_pagina in clientes_por_pagina:
                            cada_cliente_en_pagina.gestor = ejecutivo_disponible
                        
                        Cliente.objects.bulk_update(clientes_por_pagina, ['gestor'])
  
        elif "asignacion_5" in request.POST:
            ejecutivos_no_disponible    = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "NO_DISPONIBLE").values("codigo_persona_beme")
            
            ejecutivos_disponibles     = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "DISPONIBLE")

            n_ejecutivos_disponibles  = ejecutivos_disponibles.count()

            if n_ejecutivos_disponibles != 0:
                clientes    = Cliente.objects.filter(ejecutivo_cartera__codigo_persona_beme__in = [x['codigo_persona_beme'] for x in ejecutivos_no_disponible]).values_list("cli_rut", flat = True)
                n_clientes  = len(clientes)
                paginator   = Paginator(clientes, np.ceil(n_clientes/n_ejecutivos_disponibles))
                    
                for page_number, ejecutivo_disponible in enumerate(ejecutivos_disponibles, 1):
                    current_page        = paginator.get_page(page_number)
                    current_cli_ruts    = current_page.object_list
                    clientes_por_pagina = Cliente.objects.filter(cli_rut__in=current_cli_ruts)
                    for cada_cliente_en_pagina in clientes_por_pagina:
                        cada_cliente_en_pagina.gestor = ejecutivo_disponible
                        
                    Cliente.objects.bulk_update(clientes_por_pagina, ['gestor'])

        elif "asignacion_6" in request.POST:
            ejecutivos_no_disponible    = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "NO_DISPONIBLE").values("codigo_persona_beme", 
                                                                                                            'codigo_sucursal')
            
            for cada_ejecutivo_no_disponible in ejecutivos_no_disponible:
                personal_disponible     = Persona.objects.filter(modulo = persona_instance.modulo,
                                                                zona = persona_instance.zona,
                                                                status = "DISPONIBLE",
                                                                codigo_sucursal = cada_ejecutivo_no_disponible['codigo_sucursal']).exclude(cargo = "ASESOR_COMERCIAL")
                
                n_personal  = personal_disponible.count()

                if n_personal != 0:
                    clientes    = Cliente.objects.filter(ejecutivo_cartera__codigo_persona_beme = cada_ejecutivo_no_disponible['codigo_persona_beme']).values_list("cli_rut", flat=True)
                    n_clientes  = len(clientes)
                    paginator   = Paginator(clientes, np.ceil(n_clientes/n_personal))
                    
                    for page_number, personal in enumerate(personal_disponible, 1):
                        current_page    = paginator.get_page(page_number)
                        current_cli_ruts= current_page.object_list
                        clientes_por_pagina = Cliente.objects.filter(cli_rut__in=current_cli_ruts)
                        for cada_cliente_en_pagina in clientes_por_pagina:
                            cada_cliente_en_pagina.gestor = personal
                        
                        Cliente.objects.bulk_update(clientes_por_pagina, ['gestor'])

        elif "asignacion_7" in request.POST:
            ejecutivos_no_disponible    = EjecutivoComercial.objects.filter(modulo = persona_instance.modulo,
                                                                            zona = persona_instance.zona,
                                                                            status = "NO_DISPONIBLE").values("codigo_persona_beme")
            
            personal_disponible         = Persona.objects.filter(modulo = persona_instance.modulo,
                                                            zona = persona_instance.zona,
                                                            status = "DISPONIBLE").exclude(cargo = "ASESOR_COMERCIAL")
            n_personal  = personal_disponible.count()

            if n_personal != 0:
                clientes    = Cliente.objects.filter(ejecutivo_cartera__codigo_persona_beme__in = [x['codigo_persona_beme'] for x in ejecutivos_no_disponible]).values_list("cli_rut", flat = True)
                n_clientes  = len(clientes)
                paginator   = Paginator(clientes, np.ceil(n_clientes/n_personal))
                    
                for page_number, personal in enumerate(personal_disponible, 1):
                    current_page        = paginator.get_page(page_number)
                    current_cli_ruts    = current_page.object_list
                    clientes_por_pagina = Cliente.objects.filter(cli_rut__in=current_cli_ruts)
                    for cada_cliente_en_pagina in clientes_por_pagina:
                        cada_cliente_en_pagina.gestor = personal
                        
                    Cliente.objects.bulk_update(clientes_por_pagina, ['gestor'])

        elif 'asignacion_gestor' in request.POST:
            if  request.POST["asignacion_gestor"] == "":
                gestor_asignado                 = None
            else:
                codigo_persona_beme = request.POST["asignacion_gestor"]
                gestor_asignado     = Persona.objects.get(codigo_persona_beme = codigo_persona_beme)

            clientes = request.POST.getlist('cartera')
            for cada_rut in clientes:
                cliente                  = Cliente.objects.get(cli_rut = int(cada_rut))
                cliente.gestor           = gestor_asignado
                cliente.fecha_asignacion = datetime.datetime.now()
                cliente.save()

    if user_instance.groups.filter(name='Asesores').exists(): 
        if request.META['QUERY_STRING']:
            usuario_a_filtrar = request.META['QUERY_STRING'].split("=")[1]
            if Persona.objects.filter(codigo_persona_beme = usuario_a_filtrar).exists:
                clientes = Cliente.objects.filter(gestor__codigo_persona_beme = usuario_a_filtrar).order_by("-impacto_gasto_pe_hoy")
            else:
                clientes = Cliente.objects.none()
        else:
            clientes = Cliente.objects.filter(modulo_cli = persona_instance.modulo, 
                                                zona_cli = persona_instance.zona).order_by("-impacto_gasto_pe_hoy").values("cli_rut", 
                                                                                                                            "cli_nom", 
                                                                                                                            'impacto_gasto_pe_hoy', 
                                                                                                                            'estado_diario', 
                                                                                                                            'renegociacion_preaprobada', 
                                                                                                                            'impactooperacion__cant_ope', 
                                                                                                                            'ejecutivo_cartera__nombre', 
                                                                                                                            'ejecutivo_cartera__apellido', 
                                                                                                                            'ejecutivo_cartera__apellido_materno', 
                                                                                                                            'gestor__cargo', 
                                                                                                                            'gestor__nombre', 
                                                                                                                            'gestor__apellido', 
                                                                                                                            'gestor__apellido_materno', 
                                                                                                                            'oferta_simulador_riesgo')
    
    stats = create_stats_asignador(persona_instance, clientes)

    return render(request = request,
                    template_name='personas_beme/asignador_de_cartera.html',
                    context = {'info_tabla'        : clientes,
                                'stats'            : stats,
                                'user_instance'    : user_instance,
                                'permisos'         : permisos,
                                'persona_instance' : persona_instance,    
                                'persona_form'     : persona_form})

def uplodad_info_to_database(path, gestor):
    nombre_columnas = get_all_fields_from_form(FormularioClienteExcel)

    file_upload = pd.read_excel(path, sheet_name="Datos")
    df_clientes = cleaning.normalize_df(file_upload)
    df_clientes = cleaning.rename_columns_clientes(df_clientes)
    df_clientes.rename(columns={"rut_cliente": "cli_rut"}, inplace = True)
    df_clientes = df_clientes[nombre_columnas]
    
    for index, cada_cliente in df_clientes.iterrows():
        cada_cliente["gestor"] = gestor
        cliente = Cliente.objects.get(cli_rut = cada_cliente.cli_rut)
        for (key, value) in cada_cliente.to_dict().items():
            if str(value) == "nan":
                value = None
            if ('fecha' in key) and (value == None):
                value = datetime.datetime.today().date()
            if type(value) == str:
                value.strip()
                value = value.replace(" ", "_")
                value = value.replace("Á", "A")
                value = value.replace("É", "E")
                value = value.replace("Í", "I")
                value = value.replace("Ó", "O")
                value = value.replace("Ú", "U")
            setattr(cliente, key, value)
        cliente.save()

@staff_member_required
def actualizador_de_gestion(request):
    user_instance      = User.objects.get(username=request.user.username)
    persona_instance   = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos           = permisos_de_grupo(user_instance)
    upload_file_form = UploadFileForm(persona = persona_instance)

    if request.method == 'POST':
        gestor   = Persona.objects.get(codigo_persona_beme = request.POST['gestor'])

        upload_file = request.FILES['info_gestion']
        fs = FileSystemStorage()

        path = os.path.join(BASE_DIR, 'excel_files', 'gestiones_realizadas', gestor.zona, gestor.modulo, today_srt, gestor.codigo_persona_beme, upload_file.name)

        if fs.exists(path):
            fs.delete(path)
            fs.save(name = path, content = upload_file)
        else:
            fs.save(name = path, content = upload_file)

        uplodad_info_to_database(path, gestor)

    return render(request       = request,
                  template_name = 'personas_beme/actualizador_de_gestion.html',
                  context       = {'upload_file_form' : upload_file_form,
                                   'user_instance'    : user_instance,
                                   'permisos'         : permisos,
                                   'persona_instance' : persona_instance})

@staff_member_required
def panel(request):
    user_instance    = User.objects.get(username=request.user.username)
    persona_instance = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos         = permisos_de_grupo(user_instance)

    if (request.GET) and (request.GET["q"].isdigit()):
        rut_cliente = request.GET["q"]
        if Cliente.objects.filter(cli_rut = rut_cliente).exists():
            cliente = Cliente.objects.get(cli_rut = rut_cliente)
            return render(request = request,
                        template_name='personas_beme/base.html',
                        context = {'persona'  : persona, 
                                   'permisos' : permisos,
                                   'cliente'  : cliente})
    else:
        return render(request = request,
                        template_name='personas_beme/base.html',
                        context = {'user_instance'    : user_instance,
                                   'permisos'         : permisos,
                                   'persona_instance' : persona_instance})

@staff_member_required
def tabla_clientes(request):
    user_instance    = User.objects.get(username=request.user.username)
    persona_instance = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos         = permisos_de_grupo(user_instance)

    if user_instance.groups.filter(name='Asesores').exists():
        clientes = Cliente.objects.none()

    else:
        yo_contraparte = Contraparte.objects.filter(contraparte = persona_instance)
        gestores       = [cada_gestor.gestor_sin_acceso for cada_gestor in yo_contraparte]
        clientes       = Cliente.objects.filter(Q(gestor = persona_instance) | Q(gestor__in = gestores)).order_by("-impacto_gasto_pe_hoy").values("cli_rut", 
                                                                                                                            "cli_nom", 
                                                                                                                            'impacto_gasto_pe_hoy', 
                                                                                                                            'estado_diario', 
                                                                                                                            'renegociacion_preaprobada', 
                                                                                                                            'impactooperacion__cant_ope', 
                                                                                                                            'ejecutivo_cartera__nombre', 
                                                                                                                            'ejecutivo_cartera__apellido', 
                                                                                                                            'ejecutivo_cartera__apellido_materno', 
                                                                                                                            'gestor__cargo', 
                                                                                                                            'gestor__nombre', 
                                                                                                                            'gestor__apellido', 
                                                                                                                            'gestor__apellido_materno', 
                                                                                                                            'oferta_simulador_riesgo')


    return render(request       = request,
                  template_name = 'personas_beme/gestion.html',
                  context       = {'info_tabla'      : clientes,
                                   'permisos'        : permisos,
                                   'user_instance'   : user_instance,
                                   'persona_instance': persona_instance})

@staff_member_required
def detalle_oferta(request):
    user_instance       = User.objects.get(username=request.user.username)
    persona_instance    = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos            = permisos_de_grupo(user_instance)
    rut                 = int(request.GET["q"])
    ofertas             = OfertaCliente.objects.filter(cliente__cli_rut = rut).latest('fecha_de_oferta')
    resumen_operaciones = ImpactoOperacion.objects.get(cliente__cli_rut = rut)

    return render(request       = request,
                  template_name = 'personas_beme/detalle_oferta.html',
                  context       = {'info_ofertas'         : ofertas,
                                    'permisos'            : permisos,
                                    'user_instance'       : user_instance,
                                    'persona_instance'    : persona_instance,
                                    'resumen_operaciones' : resumen_operaciones})

@staff_member_required
def contrapartes(request):
    user_instance       = User.objects.get(username=request.user.username)
    persona_instance    = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos            = permisos_de_grupo(user_instance)
    contrapartes_form   = ContraparteForm(persona = persona_instance)
    contrapartes        = Contraparte.objects.all()

    if request.method == "POST":
        if 'contrapartes_button' in request.POST:
            gestor_sin_acceso = Persona.objects.get(codigo_persona_beme = request.POST['gestor_sin_acceso'])
            contraparte       = Persona.objects.get(codigo_persona_beme = request.POST['contraparte'])
            if not Contraparte.objects.filter(gestor_sin_acceso = gestor_sin_acceso, contraparte = contraparte).exists():
                relacion = Contraparte.objects.create(gestor_sin_acceso = gestor_sin_acceso, contraparte = contraparte)
                relacion.save()
            else:
                print(contrapartes_form.errors)
                
        elif 'relacion' in request.POST:
            relaciones = request.POST.getlist('relacion')
            for cada_relacion in relaciones:
                str_gestor_sin_acceso = cada_relacion.split("_")[0]
                str_contraparte       = cada_relacion.split("_")[1]

                gestor_sin_acceso = Persona.objects.get(codigo_persona_beme = str_gestor_sin_acceso)
                contraparte       = Persona.objects.get(codigo_persona_beme = str_contraparte)

                relacion          = Contraparte.objects.get(gestor_sin_acceso = gestor_sin_acceso, contraparte = contraparte)
                relacion.delete()


    return render(request       = request,
                  template_name = 'personas_beme/contrapartes.html',
                  context       = {'user_instance'     : user_instance,
                                    'persona_instance' : persona_instance,
                                    'permisos'         : permisos,
                                    'contrapartes_form': contrapartes_form,
                                    'contrapartes'     : contrapartes})

@staff_member_required
def distribucion_de_gestion(request):
    user_instance       = User.objects.get(username=request.user.username)
    persona_instance    = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos            = permisos_de_grupo(user_instance)

    tabla_con_gestion = create_table_a_gestionar(persona_instance)
    indices = tabla_con_gestion.index
    fecha = list(tabla_con_gestion["fecha"])
    gestor = list(tabla_con_gestion["gestor"])
    nombre_archivo = list(tabla_con_gestion["file_name"])

    if request.method == "POST":
        if HOST_NAME in ["w81-yaguile1", "vsk12-micro-neg"]:
            atributos_cliente   = [f.name for f in Cliente._meta.get_fields()]
            atributos_operacion = [f.name for f in Operacion._meta.get_fields()]    
            atributos_operacion.append("cli_rut")
            atributos_operacion.append("dec_cpd")
            atributos_operacion.append("n_cuota")
            atributos_operacion.append("cant_cuo")
            atributos_operacion.append("clave")
            atributos_operacion.append("dop_sdo_cst")
            atributos_operacion.append("num_ope")
            atributos_operacion.append("ope_num_mes_cuo")
            atributos_operacion.append("ope_tasa_penal")

            personas_beme = Persona.objects.filter(Q(zona = persona_instance.zona) & Q(modulo = persona_instance.modulo) & ~Q(cargo = "ASESOR_COMERCIAL"))
        
            print("va por aca")
            for cada_persona_beme in personas_beme:
                if Cliente.objects.filter(gestor = cada_persona_beme).exists():    
                    clientes = pd.DataFrame(list(Cliente.objects.filter(gestor = cada_persona_beme).values()))
                    
                    print(clientes.columns)
                    clientes["nombre_ejecutivo"]            = [Persona.objects.get(codigo_persona_beme = x).nombre for x in clientes["ejecutivo_cartera_id"]]
                    clientes["apellido_ejecutivo"]          = [Persona.objects.get(codigo_persona_beme = x).apellido for x in clientes["ejecutivo_cartera_id"]]
                    clientes["apellido_materno_ejecutivo"]  = [Persona.objects.get(codigo_persona_beme = x).apellido_materno for x in clientes["ejecutivo_cartera_id"]]
                    clientes["nombre_ejecutivo_cartera"]    = clientes["nombre_ejecutivo"].str.cat(clientes["apellido_ejecutivo"], sep = " ")
                    clientes["nombre_ejecutivo_cartera"]    = clientes["nombre_ejecutivo_cartera"].str.cat(clientes["apellido_materno_ejecutivo"], sep = " ")

                    cada_persona_beme_dict = model_to_dict(cada_persona_beme)
                    clientes_dict       = clientes.to_dict()
                    operaciones         = pd.DataFrame(list(Operacion.objects.filter(cliente__cli_rut__in = list(clientes["cli_rut"])).order_by('cliente__cli_rut').values()))
                    operaciones.reset_index(drop = True, inplace = True)
                    print(operaciones)
                    operaciones_dict    = operaciones.to_dict()
                    tasks.creador_excel_gestion_task.delay(cada_persona_beme_dict, clientes_dict, operaciones_dict, atributos_cliente, atributos_operacion)
    
    return render(request = request,
                        template_name = 'personas_beme/distribucion_de_gestion.html',
                        context = {'user_instance'      : user_instance,
                                   'permisos'           : permisos,
                                   'persona_instance'   : persona_instance,
                                   'indices'            : indices,
                                   'fecha'              : fecha,
                                   'gestor'             : gestor,
                                   'nombre_archivo'     : nombre_archivo })

@staff_member_required
def consolidado_gestion(request):
    user_instance       = User.objects.get(username=request.user.username)
    persona_instance    = Persona.objects.get(codigo_persona_beme = user_instance.username)
    permisos            = permisos_de_grupo(user_instance)

    personas_a_consolidar, list_n_clientes_asignados, list_impacto_total, list_n_clientes_asignados_con_oferta_simulador, list_n_clientes_morosos, list_impacto_morosos, list_perc_avance, list_n_morosos_contactados = create_table_consolidacion(persona_instance)
    usuario_de_personas = [persona_a_consolidar.codigo_persona_beme for persona_a_consolidar in personas_a_consolidar]
    
    indices_consolidado =list(range(len(list_n_clientes_asignados)))

    total = [sum(list_n_clientes_asignados), 
             sum(list_n_clientes_asignados_con_oferta_simulador),
             sum(list_n_clientes_morosos),
             sum(list_n_morosos_contactados),
             sum(list_perc_avance)/len(list_perc_avance),
             sum(list_impacto_total),
             sum(list_impacto_morosos) ]
    
    return render(request = request,
                        template_name = 'personas_beme/consolidado_gestion.html',
                        context = {'user_instance'                          : user_instance,
                                   'permisos'                               : permisos,
                                   'persona_instance'                       : persona_instance,
                                   'indices_consolidado'                    : indices_consolidado,
                                   'personas_a_consolidar'                  : personas_a_consolidar,
                                   'usuario_de_personas'                    : usuario_de_personas,
                                   'list_n_clientes_asignados'              : list_n_clientes_asignados,
                                   'list_impacto_total'                     : list_impacto_total,
                                   'list_n_clientes_asignados_con_oferta_simulador'   : list_n_clientes_asignados_con_oferta_simulador,
                                   'list_n_clientes_morosos'                : list_n_clientes_morosos,
                                   'list_n_morosos_contactados'             : list_n_morosos_contactados,
                                   'list_impacto_morosos'                   : list_impacto_morosos,
                                   'list_perc_avance'                       : list_perc_avance,
                                   'total'                                  : total})

@staff_member_required
def info_clientes(request):
    user_instance    = User.objects.get(username=request.user.username)
    persona_instance = Persona.objects.get(codigo_persona_beme = user_instance.username) 
    permisos         = permisos_de_grupo(user_instance)
    excel_form       = FormularioClienteExcel()
    db_form          = FormularioClienteDB()
    contrapartes     = EmailForm(gestor_sin_acceso=persona_instance)

    if request.method == "POST":
        if 'excel_button' in request.POST:
            rut        = int(request.META['QUERY_STRING'].split("=")[-1])
            cliente    = Cliente.objects.get(cli_rut = rut)
            if cliente.gestor == persona_instance:
                excel_form = FormularioClienteExcel(request.POST, instance = cliente)
                if excel_form.is_valid():
                    excel_form.save()
                else:
                    print(excel_form.errors)
            else:
                cliente.fecha_firma  = datetime.datetime.strptime(request.POST['fecha_firma'], "%d/%m/%Y").date()
                cliente.estado_curse = request.POST['estado_curse']
                cliente.save()

        if 'db_button' in request.POST:
            rut        = int(request.POST.get("cli_rut"))
            cliente    = Cliente.objects.get(cli_rut = rut)
            excel_form = FormularioClienteDB(request.POST, instance = cliente)
            if excel_form.is_valid():
                excel_form.save()
            else:
                print(excel_form.errors)

        if 'email_button' in request.POST:
            rut           = int(request.POST.get("cli_rut"))
            cliente       = Cliente.objects.get(cli_rut = rut)
            person_choice = request.POST.get("person_choice")

            eleccion_relacion_contraparte = Contraparte.objects.get(id = person_choice)
            contraparte_a_informar        = eleccion_relacion_contraparte.contraparte
            email_sender(persona_instance, contraparte_a_informar, cliente)

    if (request.GET) and (request.GET["q"].isdigit()):
        rut     = int(request.GET["q"])
        
        if Cliente.objects.filter(cli_rut = rut).exists():
            cliente    = Cliente.objects.get(cli_rut = rut)
            excel_form = FormularioClienteExcel(instance = cliente)
            db_form    = FormularioClienteDB(instance = cliente)
            if OfertaCliente.objects.filter(cliente__cli_rut = rut).exists():
                ofertas = OfertaCliente.objects.filter(cliente__cli_rut = rut).latest('fecha_de_oferta')
                detalle_operaciones = Operacion.objects.filter(cliente__cli_rut = rut)
                resumen_operaciones = ImpactoOperacion.objects.get(cliente__cli_rut = rut)
                return render(request = request,
                                template_name='personas_beme/info_clientes.html',
                                context = {'detalle_operaciones' : detalle_operaciones,
                                        'resumen_operaciones' : resumen_operaciones,
                                        'info_oferta'         : ofertas, 
                                        'info_cliente'        : cliente,
                                        'excel_form'          : excel_form,
                                        'db_form'             : db_form,
                                        'user_instance'       : user_instance,
                                        'permisos'            : permisos,
                                        'persona_instance'    : persona_instance,
                                        'contrapartes'        : contrapartes})
            else:
                return render(request = request,
                                template_name='personas_beme/info_clientes.html',
                                context = {'info_cliente'     : cliente,
                                        'excel_form'          : excel_form,
                                        'db_form'             : db_form,
                                        'user_instance'       : user_instance,
                                        'permisos'            : permisos,
                                        'persona_instance'    : persona_instance,
                                        'contrapartes'        : contrapartes})

        else:
            # acciones cuando el pedido no existe, redireccionas, envias un mensaje o cualquier opcion que consideres necesario para tratar este caso
            return render(request     = request,
                        template_name ='personas_beme/info_clientes.html',
                        context       = {'user_instance'    : user_instance,
                                         'permisos'         : permisos,
                                         'persona_instance' : persona_instance})

    else:
        return render(request         = request,
                        template_name = 'personas_beme/info_clientes.html',
                        context       = {'user_instance'    : user_instance,
                                         'permisos'         : permisos,
                                         'persona_instance' : persona_instance })