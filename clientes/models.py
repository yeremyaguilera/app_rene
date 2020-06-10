from django.db import models
import sys
sys.path.append("..")
from personas_beme.models import MODULOS_CENTRO, MODULOS_NORTE, MODULOS_SUR
from personas_beme.models import SUCURSALES_CENTRO, SUCURSALES_NORTE, SUCURSALES_SUR
from personas_beme.models import ZONAS

from personas_beme.models import EjecutivoComercial, Persona

# Create your models here.
CONTACTABILIDAD = (('CONTACTO_TITULAR_OK', 'Contacto Titular OK'), 
                    ('CONTACTO_TITULAR_OCUPADO', 'Contacto Titular Ocupado'), 
                    ('CONTACTO_TERCERO', 'Contacto Tercero'), 
                    ('NO_CONTACTADO', 'No Contactado'))

RESPUESTAS_CLIENTE = (('INTERESADO_ACEPTA_OFERTA_1_SIMULADOR'   , "Interesado - Acepta Oferta 1 Simulador"), 
                        ('INTERESADO_ACEPTA_OFERTA_2_SIMULADOR' , "Interesado - Acepta Oferta 2 Simulador"), 
                        ('INTERESADO_OTRA_RENEGOCIACION'        , "Interesado - Otra Renegociación"), 
                        ('INTERESADO_LO_PENSARA'                , "Interesado - Lo Pensará"), 
                        ('RECHAZA_TOMARA_RENEGOCIACION_WEB'     , "Rechaza - Tomará Renegociación Web"), 
                        ('RECHAZA_TOMARA_POSTERGACION'          , "Rechaza - Tomará Postergación"), 
                        ('RECHAZA_PAGARA_CUOTA'                 , "Rechaza - Pagará Cuota"), 
                        ('RECHAZA_OTRO_MOTIVO'                  , "Rechaza - Otro Motivo"), 
                        ('SIN_CONTACTO_NO_CONTESTA_LLAMADA'     , "Sin Contacto - No Contesta Llamada"), 
                        ('SIN_CONTACTO_Nº_NO_CORRESPONDE'       , "Sin Contacto - N° No Corresponde"), 
                        ('SIN_CONTACTO_FONO_SIN_SERVICIO/NO_EXISTE' , "Sin Contacto - Fono Sin Servicio/No Existe"), 
                        ('LLAMAR_DURANTE_DIA'                   , "Llamar Durante el Día"), 
                        ('ACTUALIZACION_DATOS_CLIENTE'          , "Actualización Datos Cliente"), 
                        ('INTERESADO_LLAMAR_OTRO_DIA'           , "Interesado - Llamar otro Día"))

ESTADO_NEGOCIACION = (('SE_ACERCARA_A_SUCURSAL'         , "Se acercará a la Sucursal"),
                    ('NO_PUEDE_ACERCARSE_A_SUCURSAL'    , "No puede acercarse a la Sucursal"),
                    ('ENVIADO_A_CURSE'                  , "Enviado a Curse"),
                    ('CLIENTE_DESISTE'                  , "Cliente Desiste"))

CONTACTO_CLIENTE_INTERESADO = (('AGENDADO', 'Agendado'), 
                                ('SIN_CONTACTO', "Sin Contacto"))

ESTADO_CLIENTE = (('FIRMARA_DOCUMENTOS', 'Firmará Documentos'), 
                    ('DOCUMENTOS_FIRMADOS', 'Documentos Firmados'), 
                    ('RECHAZA_OFERTA', 'Rechaza Oferta'))


ESTADO_DIARIO = (("MOROSO", "Moroso"),
                ("AL_DIA", "Al Día"))

OPCIONES_CANAL = ((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"))

OPCIONES_POSTERGACION = (("SI", "SI"), ("NO", "NO"))

class Cliente(models.Model):
    class Meta:
        ordering = ['cli_rut']
    cli_rut = models.BigIntegerField(primary_key=True, help_text="Sin dígito verificador")
    cli_nom = models.CharField(max_length=100)

    segmento            = models.CharField(max_length = 200)
    nano_segmento       = models.CharField(max_length = 200)
    micro_segmento      = models.CharField(max_length = 200)

    impacto_gasto_pe_inicial    = models.FloatField()
    impacto_gasto_pe_hoy        = models.FloatField(blank=True, null = True)

    tel_fijo_1 = models.BigIntegerField(blank=True, null = True,  help_text="+56 + (cod reg) + (num)")
    tel_fijo_2 = models.BigIntegerField(blank=True, null = True, help_text="+56 + (cod reg) + (num)")
    tel_cel_1  = models.BigIntegerField(blank=True, help_text="+569 + (123456789)")
    tel_cel_2  = models.BigIntegerField(blank=True, help_text="+569 + (123456789)")

    email               = models.EmailField(blank = True, null = True)

    direccion_particular = models.CharField(max_length = 300, blank = True, null = True)
    direccion_comercial  = models.CharField(max_length = 300, blank = True, null = True)

    zona_cli = models.CharField(max_length = 100, 
                                        choices = ZONAS, 
                                        blank = False, 
                                        null = False)

    modulo_cli = models.CharField(max_length = 100, 
                                        choices = MODULOS_NORTE + MODULOS_CENTRO + MODULOS_SUR, 
                                        blank = False, 
                                        null = False)

    sucursal_cli = models.CharField(max_length = 100)

    ejecutivo_cartera   = models.ForeignKey(EjecutivoComercial  , on_delete = models.SET_NULL, null=True, related_name='pertenece_a_la_cartera', help_text="Sólo Ejecutivo")
    gestor              = models.ForeignKey(Persona             , on_delete = models.SET_NULL, null=True, blank = True, related_name='actualmente_gestionando', help_text="Ejecutivos y Asistentes Comerciales")

    estado_diario       = models.CharField(max_length = 100, 
                                        choices = ESTADO_DIARIO,
                                        blank = True, 
                                        null = True)

    maximo_dias_mora    =  models.IntegerField(blank = True, null = True)

    saldo_moroso_hoy    = models.FloatField(blank=True, null = True)

    postergacion_cargada_hoy = models.CharField(max_length = 200, blank=True, null = True)

    criterio_seleccion_inicial = models.CharField(max_length = 200, blank=True, null = True)

    canal_postergacion_hoy = models.CharField(max_length = 200, blank=True, null = True)

    inscrito_formulario_web = models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    renegociacion_web_disponible = models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    renegociacion_preaprobada = models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    oferta_simulador_riesgo   = models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    posee_vencimiento_no_mensual   = models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    posee_operaciones_con_aval   = models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    campana_capital_covid =   models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)
    campana_postergacion_preferencial =   models.CharField(max_length = 200,
                                        blank = True, 
                                        null = True)

    fecha_asignacion_gestor     = models.DateField(null = True, blank=True)
    fecha_asignacion_foco       = models.DateField(null = True, blank=True)
    fecha_actualizacion_datos   = models.DateField(null = True, blank=True)
    
    fecha_registro          = models.DateField(null = True, blank=True) 
    
    n_gestiones             = models.IntegerField(null = True)
    n_gestiones_efectivas   = models.IntegerField(null = True)

    contactabilidad     = models.CharField(max_length = 100, 
                                        choices = CONTACTABILIDAD,
                                        blank = True, 
                                        null = True)

    respuesta_cliente   = models.CharField(max_length = 100, 
                                        choices = RESPUESTAS_CLIENTE, 
                                        blank = True, 
                                        null = True)
    
    estado_negociacion  = models.CharField(max_length = 100, 
                                        choices = ESTADO_NEGOCIACION, 
                                        blank = True, 
                                        null = True)

    observacion         = models.TextField(max_length = 500, 
                                        blank = True, 
                                        null = True)

    fecha_regula  = models.DateField(null = True, blank=True)
    max_proc = models.DateField(null = True, blank=True)
    max_otorgamiento = models.DateField(null = True, blank=True)

    ope_oto_vigente = models.IntegerField(null = True, blank = True)
    monto_oto_vigente = models.FloatField(null = True, blank = True)
    sol_otorgada = models.CharField(max_length = 100, null = True, blank = True)


    def __str__(self):
        return self.cli_nom +': '+ str(self.cli_rut)

class OfertaCliente(models.Model):
    class Meta:
        verbose_name = "Oferta Cliente"
        verbose_name_plural = "Ofertas Clientes"
        unique_together = ("fecha_de_oferta", "cliente")

    cliente           = models.ForeignKey(Cliente, on_delete = models.CASCADE, related_name='cliente')
    
    fecha_de_oferta   = models.DateField(null=False, blank=False)

    ope_tasa_oferta_1         = models.FloatField(default = 0, blank=False)
    num_cuotas_oferta_1       = models.IntegerField(null=True, default = 1, blank=False)
    monto_oferta_1            = models.IntegerField(default = 0, blank=False)
    monto_c_oferta_1          = models.IntegerField(default = 0, blank=False)
    monto_k_oferta_1          = models.IntegerField(default = 0, blank=False)
    num_cuotas_k_1            = models.IntegerField(default = 0, blank=False)
    monto_gar_1_oferta_1      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_1_oferta_1 = models.IntegerField(default = 0, blank=False)
    monto_gar_2_oferta_1      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_2_oferta_1 = models.IntegerField(default = 0, blank=False)
    monto_gar_3_oferta_1      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_3_oferta_1 = models.IntegerField(default = 0, blank=False)
    monto_gar_4_oferta_1      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_4_oferta_1 = models.IntegerField(default = 0, blank=False)
    per_rebaja_oferta_1       = models.FloatField(default = 0, blank=False)
    total_a_pagar_oferta_1    = models.IntegerField(default = 0, blank=False)

    ope_tasa_oferta_2         = models.FloatField(default = 0, blank=False)
    num_cuotas_oferta_2       = models.IntegerField(default = 1, blank=False)
    monto_oferta_2            = models.IntegerField(default = 0, blank=False)
    monto_c_oferta_2          = models.IntegerField(default = 0, blank=False)
    monto_k_oferta_2          = models.IntegerField(default = 0, blank=False)
    num_cuotas_k_2            = models.IntegerField(default = 0, blank=False)
    monto_gar_1_oferta_2      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_1_oferta_2 = models.IntegerField(default = 0, blank=False)
    monto_gar_2_oferta_2      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_2_oferta_2 = models.IntegerField(default = 0, blank=False)
    monto_gar_3_oferta_2      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_2_oferta_2 = models.IntegerField(default = 0, blank=False)
    monto_gar_4_oferta_2      = models.IntegerField(default = 0, blank=False)
    num_cuotas_gar_4_oferta_2 = models.IntegerField(default = 0, blank=False)
    per_rebaja_oferta_2       = models.FloatField(default = 0, blank=False)
    total_a_pagar_oferta_2    = models.IntegerField(default = 0, blank=False)

    def __str__(self):
        return self.cliente.__str__() + ': '+ str(self.fecha_de_oferta)
