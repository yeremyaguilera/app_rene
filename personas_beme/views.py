from django.shortcuts import render
from .models import EjecutivoComercial
from gestion.models import Contraparte
from clientes.models import Cliente, OfertaCliente
from operaciones.models import Operacion, ImpactoOperacion

from django.db.models import Q

from .forms import FormularioClienteDB, FormularioClienteExcel, EmailForm
import pyodbc
import os
import pandas.io.sql as psql
import socket
HOST_NAME = socket.gethostname().lower()
# Create your views here.
def email_sender(ejecutivo, contraparte, cliente):

    email_ejecutivo = ejecutivo.email
    nombre_ejecutivo = ejecutivo.__str__()

    email_contraparte = contraparte.email
    nombre_contraparte = contraparte.__str__()

    rut_cliente = cliente.cli_rut

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
                            <div> {}!, El cliente lalala ha aceptado una Oferta de Renegociación : <a href = "http://{}:8002/info_clientes/?q={}" >Ver Detalle</a> </div>
                            <div> La gestión fue realizada por {}.</div>
                            <div> Contacto: {}</div>
                            <br />
                            <div> Saludos, </div>
                            <div> Equipo APP RENE </div>
                            <br />
                            <br />
                            <figure>
                                <img src="{}" width="350" height="67">
                            </figure>
                        </body>
                </html>',
        @body_format = 'HTML' ;""".format(email_contraparte, nombre_contraparte, HOST_NAME, rut_cliente, nombre_ejecutivo, email_ejecutivo, figure_dir)

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


def panel(request):
    nombre_usuario = request.user.username
    ejecutivo = EjecutivoComercial.objects.get(email__startswith = nombre_usuario)
    return render(request = request,
                  template_name='personas_beme/base.html',
                  context = {"ejecutivo": ejecutivo})


def tabla_clientes(request):
    nombre_usuario = request.user.username
    ejecutivo      = EjecutivoComercial.objects.get(email__startswith = nombre_usuario)

    if request.user.username == "yaguile1":
        clientes = Cliente.objects.all().order_by("-impacto_gasto")
    else:
        nombre_usuario = request.user.username
        yo_contraparte = Contraparte.objects.filter(ejecutivo_contraparte = ejecutivo)

        ejecutivos = [cada_ejecutivo.ejecutivo_sin_acceso for cada_ejecutivo in yo_contraparte]

        clientes = Cliente.objects.filter(Q(ejecutivo_gestor = ejecutivo) | Q(ejecutivo_gestor__in = ejecutivos)).order_by("-impacto_gasto")
    return render(request = request,
                  template_name='personas_beme/gestion.html',
                  context = {"info_tabla"   : clientes,
                            "ejecutivo"     : ejecutivo})

def detalle_oferta(request):
    rut     = int(request.GET["q"])
    ofertas = OfertaCliente.objects.get(cliente__cli_rut = rut)
    resumen_operaciones = ImpactoOperacion.objects.get(cliente__cli_rut = rut)
    return render(request = request,
                  template_name='personas_beme/detalle_oferta.html',
                  context = {"info_ofertas": ofertas,
                            "resumen_operaciones": resumen_operaciones})

def info_clientes(request):
    nombre_usuario = request.user.username
    ejecutivo      = EjecutivoComercial.objects.get(email__startswith = nombre_usuario)    
    excel_form     = FormularioClienteExcel()
    db_form        = FormularioClienteDB()
    contrapartes   = EmailForm(ejecutivo_sin_acceso=ejecutivo)

    if request.method == "POST":
        if 'excel_button' in request.POST:
            rut     = int(request.POST.get("cli_rut"))
            cliente = Cliente.objects.get(cli_rut = rut)
            excel_form    = FormularioClienteExcel(request.POST, instance = cliente)
            if excel_form.is_valid():
                excel_form.save()
            else:
                print(excel_form.errors)

        if 'db_button' in request.POST:
            rut     = int(request.POST.get("cli_rut"))
            cliente = Cliente.objects.get(cli_rut = rut)
            excel_form    = FormularioClienteDB(request.POST, instance = cliente)
            if excel_form.is_valid():
                excel_form.save()
            else:
                print(excel_form.errors)

        if 'email_button' in request.POST:
            rut     = int(request.POST.get("cli_rut"))
            cliente = Cliente.objects.get(cli_rut = rut)
            person_choice = request.POST.get("person_choice")
            eleccion_relacion_contraparte   = Contraparte.objects.get(id = person_choice)
            contraparte_a_informar = eleccion_relacion_contraparte.ejecutivo_contraparte
            email_sender(ejecutivo, contraparte_a_informar, cliente)

        
    if request.GET:
        rut     = int(request.GET["q"])
        
        if Cliente.objects.filter(cli_rut = rut).exists():
            cliente = Cliente.objects.get(cli_rut = rut)

            excel_form = FormularioClienteExcel(instance = cliente)
            db_form    = FormularioClienteDB(instance = cliente)

            ofertas = OfertaCliente.objects.get(cliente__cli_rut = rut)
            detalle_operaciones = Operacion.objects.filter(cliente__cli_rut = rut)
            resumen_operaciones = ImpactoOperacion.objects.get(cliente__cli_rut = rut)
            return render(request = request,
                            template_name='personas_beme/info_clientes.html',
                            context = {"detalle_operaciones" : detalle_operaciones,
                                        "resumen_operaciones": resumen_operaciones,
                                        "info_oferta"        : ofertas, 
                                        "info_cliente"       : cliente,
                                        "excel_form"         : excel_form,
                                        "db_form"            : db_form,
                                        "ejecutivo"          : ejecutivo,
                                        "contrapartes"       : contrapartes})
        else:
            # acciones cuando el pedido no existe, redireccionas, envias un mensaje o cualquier opcion que consideres necesario para tratar este caso
            return render(request     = request,
                        template_name ='personas_beme/info_clientes.html',
                        context       = {"ejecutivo": ejecutivo})

    else:
        return render(request         = request,
                        template_name = 'personas_beme/info_clientes.html',
                        context       = {"ejecutivo": ejecutivo})