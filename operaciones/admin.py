from django.contrib import admin
from .models import Operacion, ImpactoOperacion
# Register your models here.


@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):

    search_fields = ('dop_num_ope', 'cliente__cli_rut')

    list_display_links = ('dop_num_ope', 'cliente')

    list_display = ('dop_num_ope',
                    'cliente',
                    'ope_cant_cuo',
                    'dop_mnt_cuo',
                    'dop_sdo_tot',
                    'ope_tasa',
                    'ope_tasa_penal_diaria',
                    'ope_cuotas_pagadas',
                    'dop_dia_mra',
                    'fecha_curse',
                    'fec_oto',
                    'primer_ven',
                    'prox_ven',
                    'fecha_pago_final',
                    'familia',
                    'cpd',
                    'marca',
                    'perfil_de_riesgo',
                    'ope_monto_origen_pes')
    pass


@admin.register(ImpactoOperacion)
class ImpactoOperacionAdmin(admin.ModelAdmin):
    search_fields = ('cliente__cli_rut','cliente__cli_nom',)
    list_display = ('cliente',
                    'fecha_de_impacto',
                    'cant_ope',
                    'plazo_restante',
                    'tasa_seguro',
                    'interes_moratorio',
                    'gastos_cobranza',
                    'comision_prep',
                    'periodo_de_gracia',
                    'saldo_adeudado_gar_final',
                    'saldo_sin_gar_comercial',
                    'saldo_sin_gar_comercial_final',
                    'saldo_adeudado_consumo',
                    'pago_mensual',
                    'ope_tasa_media',
                    'total_a_pagar_hoy',
                    'perfil_riesgo')
    pass
