from django.db import models
from clientes.models import Cliente
# Create your models here.
PERFILES_RIESGO = (("EXCELENTE", "Excelente"), ("BUENO", "Bueno"), ("REGULAR", "Regular"), ("MALO", "Malo"))

familias = ['MR', 'M', 'MG', 'MRG', 'RP', 'MF', 'TC', 'LCC', 'LCK', 'MRF', 'NRJ', 'CV', 'CK']
FAMILIAS = (zip(familias, familias))

class Operacion(models.Model):
    class Meta:
        verbose_name = "Operacion"
        verbose_name_plural = "Operaciones"

    dop_num_ope = models.IntegerField(primary_key=True, verbose_name="Número de Operación")

    cliente = models.ForeignKey(Cliente,  on_delete = models.CASCADE)

    ope_cant_cuo         = models.IntegerField(verbose_name="Plazo")
    dop_mnt_cuo          = models.IntegerField(verbose_name="Monto Cuota")
    dop_sdo_tot          = models.IntegerField(verbose_name="Saldo Total")
    ope_tasa             = models.FloatField(verbose_name="Tasa")
    ope_tasa_penal_diaria = models.FloatField(verbose_name="Tasa Penal Diaria")
    ope_cuotas_pagadas   = models.IntegerField(verbose_name="Cuotas Pagadas")
    ope_monto_origen_pes = models.IntegerField(verbose_name="Monto Origen")
    eficacia_gar         = models.FloatField(verbose_name="Eficacia de la Garantía")

    dop_dia_mra          = models.IntegerField(verbose_name="Días de Mora")

    fecha_curse          = models.DateField(blank=True, verbose_name="Fecha Curse")
    fec_oto              = models.DateField(blank=True, verbose_name="Fecha Otorgación")
    primer_ven           = models.DateField(blank=True, verbose_name="Primer Vencimiento")
    prox_ven             = models.DateField(blank=True, verbose_name="Próximo Vencimiento")
    fecha_pago_final     = models.DateField(blank=True)

    familia              = models.CharField(max_length = 20, 
                                        choices = FAMILIAS, 
                                        blank = False)
    cpd = models.CharField(max_length = 5, blank = False)


    marca = models.CharField(max_length = 20, 
                                        choices = (("C", "C"), ("K", "K")), 
                                        blank = False, verbose_name="Tipo de Crédito")


    perfil_de_riesgo       = models.CharField(max_length = 20, 
                                        choices = PERFILES_RIESGO, 
                                        blank = False)

    def __str__(self):
        return str(self.dop_num_ope)





class ImpactoOperacion(models.Model):
    class Meta:
        verbose_name = "Impacto de Operacion"
        verbose_name_plural = "Impacto de Operaciones"
        unique_together = ("cliente", "fecha_de_impacto")

    cliente           = models.OneToOneField(Cliente,  on_delete = models.CASCADE)

    fecha_de_impacto  = models.DateField(null=False, blank=False)

    cant_ope          = models.IntegerField(default = 1, blank=False)

    plazo_restante    = models.IntegerField(default = 1, blank=False)

    tasa_seguro       = models.FloatField(default = 0, blank=True, null=True)

    interes_moratorio = models.IntegerField(default = 1, blank=False)

    gastos_cobranza   = models.IntegerField(default = 0, blank=False)

    comision_prep     = models.IntegerField(default = 0, blank=False)

    periodo_de_gracia = models.IntegerField(default = 0, blank=False)

    saldo_adeudado_gar   = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_1 = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_2 = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_3 = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_4 = models.IntegerField(default = 0, blank=False)

    saldo_adeudado_gar_final   = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_1_final = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_2_final = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_3_final = models.IntegerField(default = 0, blank=False)
    saldo_adeudado_gar_4_final = models.IntegerField(default = 0, blank=False)

    saldo_sin_gar_comercial       = models.IntegerField(default = 0, blank=True, null=True)
    saldo_sin_gar_comercial_final = models.IntegerField(default = 0, blank=True, null=True)

    saldo_adeudado_consumo       = models.IntegerField(default = 0, blank=True, null=True)
    saldo_adeudado_consumo_final = models.IntegerField(default = 0, blank=True, null=True)

    num_cuotas_max_k            = models.IntegerField(default = 0, blank=True, null=True)
    num_cuotas_max_fogape_gar_1 = models.IntegerField(default = 0, blank=True, null=True)
    num_cuotas_max_fogape_gar_2 = models.IntegerField(default = 0, blank=True, null=True)
    num_cuotas_max_fogape_gar_3 = models.IntegerField(default = 0, blank=True, null=True)
    num_cuotas_max_fogape_gar_4 = models.IntegerField(default = 0, blank=True, null=True)


    pago_mensual = models.IntegerField(default = 0, blank=False)

    ope_tasa_media = models.FloatField(default = 0, blank=False)
    
    total_a_pagar_hoy = models.IntegerField(default = 0, blank=False)

    perfil_riesgo = models.CharField(max_length = 20, 
                                        choices = PERFILES_RIESGO, 
                                        blank = False)

    def __str__(self):
        return str(self.cliente)
