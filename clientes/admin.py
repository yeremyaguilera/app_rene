from django.contrib import admin
from .models import Cliente, OfertaCliente
from personas_beme.admin import ExportXLSXMixin
# Register your models here.
@admin.register(Cliente)
class PersonaAdmin(admin.ModelAdmin, ExportXLSXMixin):

    list_display_links = ('cli_rut', 'cli_nom')

    search_fields = ('cli_rut', 'cli_nom')

    actions = ["export_as_xlsx"]

    list_display = ('cli_rut',
                    'cli_nom',
                    'impacto_gasto',
                    'tel_fijo_1',
                    'tel_fijo_2',
                    'tel_cel_1',
                    'tel_cel_2',
                    'ejecutivo_cartera',
                    'ejecutivo_gestor',
                    'zona_cli',
                    'modulo_cli',
                    'sucursal_cli')

    list_filter = ('zona_cli', 'modulo_cli', 'sucursal_cli')

    fieldsets = (('Información del Cliente',
                                            {'fields': (('cli_rut'    , 'cli_nom', 'impacto_gasto'),
                                                        ('tel_fijo_1', 'tel_fijo_2', 'tel_cel_1', 'tel_cel_2'),
                                                        ('direccion_particular', 'direccion_comercial'),
                                                        'zona_cli'  , 'modulo_cli', 'sucursal_cli',
                                                        'ejecutivo_cartera', 'ejecutivo_gestor', 'estado_diario', 'postergacion','canal_ccl', 'canal_web')}),
                 ('Información de Gestión',
                                            {'fields': (('fecha_asignacion', 'fecha_gestion'),
                                                        'contactabilidad', 'respuesta_cliente', 'estado', 'fecha_reinsistencia', 
                                                        'contacto_cliente_interesado', 'estado_cliente', 'fecha_firma', 
                                                        'estado_curse', 'eleccion_oferta')}))

@admin.register(OfertaCliente)
class OfertaClienteAdmin(admin.ModelAdmin):

    list_filter = ('cliente__zona_cli', 'cliente__ejecutivo_gestor',)

    def ft_monto_oferta_1(self, obj):
        return '$ {:,}'.format(obj.monto_oferta_1)

    def ft_monto_oferta_2(self, obj):
        return '$ {:,}'.format(obj.monto_oferta_2)

    def ft_total_a_pagar_oferta_1(self, obj):
        return '$ {:,}'.format(obj.total_a_pagar_oferta_1)
        
    def ft_total_a_pagar_oferta_2(self, obj):
        return '$ {:,}'.format(obj.total_a_pagar_oferta_2)

    def tasa_oferta_1(self, obj):
        return '{:.2%}'.format(obj.ope_tasa_oferta_1)

    def tasa_oferta_2(self, obj):
        return '{:.2%}'.format(obj.ope_tasa_oferta_1)

    def rebaja_oferta_1(self, obj):
        return '{:.2%}'.format(obj.per_rebaja_oferta_1)

    def rebaja_oferta_2(self, obj):
        return '{:.2%}'.format(obj.per_rebaja_oferta_2)

    search_fields = ('cliente__cli_rut', 'cliente__cli_nom')

    list_display = ('cliente',
                    'fecha_de_oferta',
                    'tasa_oferta_1',
                    'plazo_oferta_1',
                    'ft_monto_oferta_1',
                    'rebaja_oferta_1',
                    'ft_total_a_pagar_oferta_1',
                    'tasa_oferta_2',
                    'plazo_oferta_2',
                    'ft_monto_oferta_2',
                    'rebaja_oferta_2',
                    'ft_total_a_pagar_oferta_2')


    date_hierarchy = 'fecha_de_oferta'

    fieldsets = (('Información',
                                            {'fields': (('cliente'    , 'fecha_de_oferta'))}),
                 ('Oferta 1',
                                            {'fields': (('ope_tasa_oferta_1'    , 'plazo_oferta_1'),
                                                        ('monto_oferta_1', 'per_rebaja_oferta_1', 'total_a_pagar_oferta_1'))}),
                 ('Oferta 2',
                                            {'fields': (('ope_tasa_oferta_2'    , 'plazo_oferta_2'),
                                                        ('monto_oferta_2', 'per_rebaja_oferta_2', 'total_a_pagar_oferta_2'))}))

    pass


