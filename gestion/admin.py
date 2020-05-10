from django.contrib import admin
from .models import Contraparte, ActualizaGestion
# Register your models here.
@admin.register(Contraparte)
class ContraparteAdmin(admin.ModelAdmin):


    search_fields = ('ejecutivo_sin_acceso__nombre', 'ejecutivo_sin_acceso__apellido', 'ejecutivo_sin_acceso__apellido_materno', 
                        'ejecutivo_contraparte__nombre', 'ejecutivo_contraparte__apellido', 'ejecutivo_contraparte__apellido_materno')

    list_display = ('ejecutivo_sin_acceso',
                    'ejecutivo_contraparte')
    pass


@admin.register(ActualizaGestion)
class ActualizaGestionAdmin(admin.ModelAdmin):
    search_fields = ('ejecutivo__nombre', 'ejecutivo__apellido', 'ejecutivo__apellido_materno')

    list_display = ('ejecutivo',
                    'fecha')
    pass