from django.contrib import admin
from .models import Contraparte
from .models import ActualizaGestion
from personas_beme.models import Persona
from django.contrib.auth.models import User
# Register your models here.
@admin.register(Contraparte)
class ContraparteAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_instance    = User.objects.get(username=request.user.username)
        persona_instance = Persona.objects.get(codigo_persona_beme = user_instance.username) 

        if db_field.name in ["gestor_sin_acceso", "contraparte"]:
            kwargs["queryset"] = Persona.objects.filter(cargo__in= ["EJECUTIVO_COMERCIAL", "ASISTENTE_COMERCIAL"], zona = persona_instance.zona, modulo = persona_instance.modulo).order_by('cargo', 'nombre')
        return super(ContraparteAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
            
    search_fields = ('gestor_sin_acceso__nombre', 'gestor_sin_acceso__apellido', 'gestor_sin_acceso__apellido_materno', 
                        'contraparte__nombre', 'contraparte__apellido', 'contraparte__apellido_materno')

    list_display = ('gestor_sin_acceso',
                    'contraparte')
    pass


@admin.register(ActualizaGestion)
class ActualizaGestionAdmin(admin.ModelAdmin):
    search_fields = ('gestor__nombre', 'gestor__apellido', 'gestor__apellido_materno')

    list_display = ('gestor',
                    'fecha')
    pass