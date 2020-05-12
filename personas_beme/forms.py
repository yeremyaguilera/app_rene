from django import forms
from clientes.models import Cliente
from gestion.models import Contraparte
from django.contrib.admin.widgets import AdminDateWidget
from clientes.models import RESPUESTAS_CLIENTE, CONTACTO_CLIENTE_INTERESADO



class FormularioClienteDB(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['cli_rut',
                    'canal_ccl',
                    'canal_web',
                    'eleccion_oferta']
                    
        widgets = {'cli_rut': forms.HiddenInput()}

class FormularioClienteExcel(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['cli_rut', 
                    'fecha_asignacion',
                    'fecha_gestion',
                    'contactabilidad',
                    'respuesta_cliente',
                    'estado',
                    'fecha_reinsistencia',
                    'contacto_cliente_interesado',
                    'estado_cliente',
                    'fecha_firma',
                    'estado_curse']
                    
        widgets = {'cli_rut': forms.HiddenInput(), 
                    'fecha_asignacion': AdminDateWidget(), 
                    'fecha_gestion': AdminDateWidget(), 
                    'fecha_reinsistencia': AdminDateWidget(), 
                    'fecha_firma': AdminDateWidget()}



class EmailForm(forms.Form):
    person_choice = forms.ModelChoiceField(required = False, queryset=Contraparte.objects.all(), label="Relación Contraparte ")

    def __init__(self, ejecutivo_sin_acceso=None, **kwargs):
        super(EmailForm, self).__init__(**kwargs)
        if ejecutivo_sin_acceso:
            self.fields['person_choice'].queryset = Contraparte.objects.filter(ejecutivo_sin_acceso=ejecutivo_sin_acceso)