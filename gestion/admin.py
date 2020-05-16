from django.contrib import admin
from .models import Contraparte
from .models import ActualizaGestion
# Register your models here.
@admin.register(Contraparte)
class ContraparteAdmin(admin.ModelAdmin):


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