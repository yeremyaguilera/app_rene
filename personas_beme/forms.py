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
        fields = ['cli_rut',]
                    
        widgets = {'cli_rut': forms.HiddenInput()}

class FormularioClienteExcel(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['cli_rut',
                    'fecha_registro',
                    'contactabilidad',
                    'respuesta_cliente',
                    'estado_negociacion',
                    'observacion']
                    
        widgets = {'cli_rut': forms.HiddenInput(), 
                    'fecha_asignacion_gestor': AdminDateWidget(), 
                    'fecha_registro': AdminDateWidget()}

class ContraparteForm(forms.ModelForm):
    class Meta:
        model = Contraparte
        fields = ['gestor_sin_acceso',
                    'contraparte']

    def __init__(self, persona=None, **kwargs):
        super(ContraparteForm, self).__init__(**kwargs)
        if persona:
            self.fields['gestor_sin_acceso'].queryset   = Persona.objects.filter(Q(zona = persona.zona) & Q(modulo = persona.modulo) & ~Q(cargo = "ASESOR_COMERCIAL")).order_by('cargo', 'nombre')
            self.fields['contraparte'].queryset         = Persona.objects.filter(Q(zona = persona.zona) & Q(modulo = persona.modulo) & ~Q(cargo = "ASESOR_COMERCIAL")).order_by('cargo', 'nombre')

class EmailForm(forms.Form):
    person_choice = forms.ModelChoiceField(required = False, queryset=Contraparte.objects.all(), label="Relación Contraparte ")

    def __init__(self, gestor_sin_acceso=None, **kwargs):
        super(EmailForm, self).__init__(**kwargs)
        if gestor_sin_acceso:
            self.fields['person_choice'].queryset = Contraparte.objects.filter(gestor_sin_acceso=gestor_sin_acceso).order_by('contraparte__cargo', 'contraparte__nombre')


class PersonaForm(forms.Form):
    asignacion_gestor = forms.ModelChoiceField(required = False, queryset=Persona.objects.all(), label="Asignación de Gestor ")

    def __init__(self, persona=None, **kwargs):
        super(PersonaForm, self).__init__(**kwargs)
        if persona:
            self.fields['asignacion_gestor'].queryset = Persona.objects.filter(Q(zona = persona.zona) & Q(modulo = persona.modulo) & ~Q(cargo = "ASESOR_COMERCIAL")).order_by('cargo', 'nombre')


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = ActualizaGestion
        fields = ['gestor',
                    'info_gestion']

    def __init__(self, persona=None, **kwargs):
        super(UploadFileForm, self).__init__(**kwargs)
        if persona:
            self.fields['gestor'].queryset = Persona.objects.filter(Q(zona = persona.zona) & Q(modulo = persona.modulo) & ~Q(cargo = "ASESOR_COMERCIAL")).order_by('cargo', 'nombre')