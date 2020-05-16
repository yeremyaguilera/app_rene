from django import forms
from clientes.models import Cliente
from personas_beme.models import Persona
from gestion.models import Contraparte, ActualizaGestion
from django.contrib.admin.widgets import AdminDateWidget
from clientes.models import RESPUESTAS_CLIENTE, CONTACTO_CLIENTE_INTERESADO
from django.db.models import Q


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

    def __init__(self, gestor_sin_acceso=None, **kwargs):
        super(EmailForm, self).__init__(**kwargs)
        if gestor_sin_acceso:
            self.fields['person_choice'].queryset = Contraparte.objects.filter(gestor_sin_acceso=gestor_sin_acceso)


class PersonaForm(forms.Form):
    asignacion_gestor = forms.ModelChoiceField(required = False, queryset=Persona.objects.all(), label="Asignación de Gestor ")

    def __init__(self, persona=None, **kwargs):
        super(PersonaForm, self).__init__(**kwargs)
        if persona:
            self.fields['asignacion_gestor'].queryset = Persona.objects.filter(Q(zona = persona.zona) & Q(modulo = persona.modulo) & ~Q(cargo = "ASESOR_COMERCIAL"))


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = ActualizaGestion
        fields = ['gestor',
                    'info_gestion']

    def __init__(self, persona=None, **kwargs):
        super(UploadFileForm, self).__init__(**kwargs)
        if persona:
            self.fields['gestor'].queryset = Persona.objects.filter(Q(zona = persona.zona) & Q(modulo = persona.modulo) & ~Q(cargo = "ASESOR_COMERCIAL"))