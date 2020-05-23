from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import EjecutivoComercial, Persona
from gestion.models import Contraparte
from clientes.models import Cliente, OfertaCliente
from operaciones.models import Operacion, ImpactoOperacion
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage

import datetime
today_srt = datetime.datetime.today().date().strftime("%d-%m-%Y")

from django.db.models import Q

from .forms import FormularioClienteDB, FormularioClienteExcel, EmailForm, UploadFileForm, PersonaForm, ContraparteForm
import pyodbc
import os
import pandas.io.sql as psql
import socket
HOST_NAME = socket.gethostname().lower()
# Create your views here.
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
    oferta_elegida = cliente.eleccion_oferta

    if email_contraparte == "":
        email_contraparte = 'yaguile1@microempresas.bancoestado.cl'

    # Carga de la imagen asociada al email
    figure_dir = os.getcwd() + "\\static\\firma.png"
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
        @body_format = 'HTML' ;""".format(email_contraparte, nombre_contraparte, nombre_cliente, oferta_elegida, HOST_NAME, rut_cliente, nombre_ejecutivo, email_ejecutivo, figure_dir)

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

@staff_member_required
def asignador_de_cartera(request):
    user_instance      = User.objects.get(username=request.user.username)
    persona_instance   = Persona.objects.get(codigo_persona_beme = user_instance.username)
    persona_form       = PersonaForm(persona = persona_instance)
    permisos           = permisos_de_grupo(user_instance)

    if request.POST:
        clientes_elegidos = request.POST.getlist('cartera')
        if request.POST["asignacion_gestor"] == "":
            gestor_asignado = None
        else:
            codigo_persona_beme = request.POST["asignacion_gestor"]
            gestor_asignado  = Persona.objects.get(codigo_persona_beme = codigo_persona_beme)
        for cada_rut in clientes_elegidos:
            cliente                  = Cliente.objects.get(cli_rut = int(cada_rut))
            cliente.gestor           = gestor_asignado
            cliente.fecha_asignacion = datetime.datetime.now()
            cliente.save()

    if user_instance.username == "yaguile1":
        clientes = Cliente.objects.all().order_by("-impacto_gasto")


    elif user_instance.groups.filter(name='Asesores').exists():
        clientes = Cliente.objects.filter(Q(modulo_cli = persona_instance.modulo) & Q(zona_cli = persona_instance.zona)).order_by("-impacto_gasto")

    return render(request = request,
                    template_name='personas_beme/asignador_de_cartera.html',
                    context = {'info_tabla'        : clientes,
                                'user_instance'    : user_instance,
                                'permisos'         : permisos,
                                'persona_instance' : persona_instance,    
                                'persona_form'     : persona_form})

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
        path = 'gestiones/{}/{}/{}'.format(today_srt, gestor.codigo_persona_beme, upload_file.name)

        if fs.exists(path):
            fs.delete(path)
            fs.save(name = path, content = upload_file)
        else:
            fs.save(name = path, content = upload_file)

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

    if user_instance.username == "yaguile1":
        clientes = Cliente.objects.all().order_by("-impacto_gasto")

    elif user_instance.groups.filter(name='Asesores').exists():
        clientes = Cliente.objects.none()

    else:
        yo_contraparte = Contraparte.objects.filter(contraparte = persona_instance)
        gestores       = [cada_gestor.gestor_sin_acceso for cada_gestor in yo_contraparte]
        clientes       = Cliente.objects.filter(Q(gestor = persona_instance) | Q(gestor__in = gestores)).order_by("-impacto_gasto")

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