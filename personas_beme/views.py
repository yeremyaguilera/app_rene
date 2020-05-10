from django.shortcuts import render
from .models import EjecutivoComercial
from clientes.models import Cliente, OfertaCliente
from operaciones.models import Operacion, ImpactoOperacion

from .forms import FormularioCliente

# Create your views here.
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
        clientes = Cliente.objects.filter(ejecutivo_gestor__email__startswith = nombre_usuario).order_by("-impacto_gasto")
        print(clientes.query)
        print(clientes)
    return render(request = request,
                  template_name='personas_beme/gestion.html',
                  context = {"info_tabla"   : clientes,
                            "ejecutivo"     : ejecutivo})

def formulario(request):
    if request.method == 'POST':
        form = FormularioCliente(request.POST or None)
    else:
        form = FormularioCliente()

    return render(request = request,
                    template_name='personas_beme/test.html',
                    context = {"form": form})

def info_clientes(request):
    nombre_usuario = request.user.username
    ejecutivo      = EjecutivoComercial.objects.get(email__startswith = nombre_usuario)    
    form           = FormularioCliente()

    if request.method == "POST":
        rut     = int(request.POST.get("cli_rut"))
        cliente = Cliente.objects.get(cli_rut = rut)
        form    = FormularioCliente(request.POST, instance = cliente)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        
    if request.GET:
        rut     = int(request.GET["q"])
        
        if Cliente.objects.filter(cli_rut = rut).exists():
            cliente = Cliente.objects.get(cli_rut = rut)
            # resto de acciones cuando el pedido existe        form    = FormularioCliente(instance = cliente)

            form = FormularioCliente(instance = cliente)
            ofertas = OfertaCliente.objects.get(cliente__cli_rut = rut)
            detalle_operaciones = Operacion.objects.filter(cliente__cli_rut = rut)
            resumen_operaciones = ImpactoOperacion.objects.get(cliente__cli_rut = rut)
            return render(request = request,
                            template_name='personas_beme/info_clientes.html',
                            context = {"detalle_operaciones" : detalle_operaciones,
                                        "resumen_operaciones": resumen_operaciones,
                                        "info_oferta"        : ofertas, 
                                        "info_cliente"       : cliente,
                                        "form"               : form,
                                        "ejecutivo"          : ejecutivo})
        else:
            # acciones cuando el pedido no existe, redireccionas, envias un mensaje o cualquier opcion que consideres necesario para tratar este caso
            return render(request     = request,
                        template_name ='personas_beme/info_clientes.html',
                        context       = {"ejecutivo": ejecutivo})

    else:
        return render(request         = request,
                        template_name = 'personas_beme/info_clientes.html',
                        context       = {"ejecutivo": ejecutivo})