from django.contrib import admin
from personas_beme.models import EjecutivoComercial, Persona
from .models import Cliente, OfertaCliente
from personas_beme.admin import ExportXLSXMixin
from django.db.models import Q
# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin, ExportXLSXMixin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ejecutivo_cartera":
            if 'add' not in request.META['PATH_INFO']:
                cli_rut = int(request.META['PATH_INFO'].split("/")[-3])
                cliente = Cliente.objects.get(cli_rut = cli_rut)
                kwargs["queryset"] = EjecutivoComercial.objects.filter(Q(zona=cliente.zona_cli) & Q(modulo=cliente.modulo_cli)).order_by('nombre')

        if db_field.name == "gestor":
            if 'add' not in request.META['PATH_INFO']:
                cli_rut = int(request.META['PATH_INFO'].split("/")[-3])
                cliente = Cliente.objects.get(cli_rut = cli_rut)
                kwargs["queryset"] = Persona.objects.filter(Q(zona=cliente.zona_cli) & Q(modulo=cliente.modulo_cli) & Q(cargo__in= ["EJECUTIVO_COMERCIAL", "ASISTENTE_COMERCIAL"])).order_by('cargo', 'nombre')
        return super(ClienteAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_display_links = ('cli_rut', 'cli_nom')

    search_fields = ('cli_rut', 'cli_nom')

    actions = ["export_as_xlsx"]

    list_display = ('cli_rut',
                    'cli_nom',
                    'impacto_gasto_pe_inicial',
                    'tel_fijo_1',
                    'tel_fijo_2',
                    'tel_cel_1',
                    'tel_cel_2',
                    'ejecutivo_cartera',
                    'gestor',
                    'zona_cli',
                    'modulo_cli',
                    'sucursal_cli')

    list_filter = ('modulo_cli',)

    fieldsets = (('Información del Cliente',
                                            {'fields': (('cli_rut' , 'cli_nom'),
                                                        ('segmento', 'nano_segmento', 'micro_segmento'),
                                                        ('impacto_gasto_pe_inicial', 'impacto_gasto_pe_hoy'),
                                                        ('tel_fijo_1', 'tel_fijo_2', 'tel_cel_1', 'tel_cel_2', 'email'),
                                                        ('direccion_particular', 'direccion_comercial'),
                                                        'zona_cli', 
                                                        'modulo_cli',
                                                        'sucursal_cli',
                                                        'ejecutivo_cartera',
                                                        'estado_diario',
                                                        'maximo_dias_mora',
                                                        'saldo_moroso_hoy',
                                                        'postergacion_cargada_hoy',
                                                        'criterio_seleccion_inicial',
                                                        'canal_postergacion_hoy', 
                                                        'inscrito_formulario_web', 
                                                        'renegociacion_web_disponible', 
                                                        'renegociacion_preaprobada',
                                                        'oferta_simulador_riesgo',
                                                        'posee_vencimiento_no_mensual',
                                                        'posee_operaciones_con_aval',
                                                        'campana_capital_covid',
                                                        'campana_postergacion_preferencial')}),
                 ('Información de Gestión',
                                            {'fields': ('gestor',
                                                        'n_gestiones',
                                                        'n_gestiones_efectivas',
                                                        'fecha_asignacion_gestor',
                                                        'fecha_asignacion_foco',
                                                        'fecha_actualizacion_datos',
                                                        'fecha_registro',
                                                        'contactabilidad', 
                                                        'respuesta_cliente', 
                                                        'estado_negociacion', 
                                                        'observacion',
                                                        'fecha_regula',
                                                        'max_proc',
                                                        'max_otorgamiento',
                                                        'ope_oto_vigente',
                                                        'monto_oto_vigente',
                                                        'sol_otorgada')}))

@admin.register(OfertaCliente)
class OfertaClienteAdmin(admin.ModelAdmin):

    list_filter = ('cliente__zona_cli', 'cliente__gestor',)

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
                    'num_cuotas_oferta_1',
                    'ft_monto_oferta_1',
                    'rebaja_oferta_1',
                    'ft_total_a_pagar_oferta_1',
                    'tasa_oferta_2',
                    'num_cuotas_oferta_2',
                    'ft_monto_oferta_2',
                    'rebaja_oferta_2',
                    'ft_total_a_pagar_oferta_2')


    date_hierarchy = 'fecha_de_oferta'

    fieldsets = (('Información',
                                            {'fields': (('cliente'    , 'fecha_de_oferta'))}),
                 ('Oferta 1',
                                            {'fields': (('ope_tasa_oferta_1'    , 'num_cuotas_oferta_1'),
                                                        ('monto_oferta_1', 'per_rebaja_oferta_1', 'total_a_pagar_oferta_1'))}),
                 ('Oferta 2',
                                            {'fields': (('ope_tasa_oferta_2'    , 'num_cuotas_oferta_2'),
                                                        ('monto_oferta_2', 'per_rebaja_oferta_2', 'total_a_pagar_oferta_2'))}))

    pass


