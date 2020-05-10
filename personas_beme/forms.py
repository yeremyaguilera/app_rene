from django import forms
from clientes.models import Cliente
from django.contrib.admin.widgets import AdminDateWidget
from clientes.models import RESPUESTAS_CLIENTE, CONTACTO_CLIENTE_INTERESADO


class FormularioCliente(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['cli_rut', 
                    'respuesta',
                    'fecha_asignacion',
                    'fecha_gestion',
                    'fecha_reinsistencia',
                    'estado_contacto_interesado',
                    'fecha_firma',
                    'postergacion',
                    'canal_ccl',
                    'canal_web']
        widgets = {'cli_rut': forms.HiddenInput(), 
                    'fecha_asignacion': AdminDateWidget(), 
                    'fecha_gestion': AdminDateWidget(), 
                    'fecha_reinsistencia': AdminDateWidget(), 
                    'fecha_firma': AdminDateWidget()}