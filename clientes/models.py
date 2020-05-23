from django.db import models
import sys
sys.path.append("..")
from personas_beme.models import MODULOS_CENTRO, MODULOS_NORTE, MODULOS_SUR
from personas_beme.models import SUCURSALES_CENTRO, SUCURSALES_NORTE, SUCURSALES_SUR
from personas_beme.models import ZONAS

from personas_beme.models import EjecutivoComercial, Persona

# Create your models here.
CONTACTABILIDAD = (('CON_CONTACTO', 'Contactado'), 
                    ('SIN_CONTACTO', 'Sin Contacto'))

RESPUESTAS_CLIENTE = (("INTERESADO_EN_OFERTA_SIMULADOR", 'Interesado en Oferta Simulador'), 
                        ('INTERESADO_EN_RENEGOCIAR_-_DERIVAR_A_PLATAFORMA_BEME', 'Interesado en Renegociar - Derivar a la Plataforma BEME'), 
                        ('NO_INTERESADO_-_PAGARA_CUOTA', 'No Interesado - Pagará Cuota'))

ESTADO = (("SE_ACERCARA_A_SUCURSAL", "Se acercará a la Sucursal"),
                    ("NO_PUEDE_ACERCARSE_A_SUCURSAL ", "No puede acercarse a la Sucursal"),
                    ("LO_PENSARA", "Lo Pensará"))

CONTACTO_CLIENTE_INTERESADO = (('AGENDADO', 'Agendado'), 
                                ('SIN_CONTACTO', "Sin Contacto"))

ESTADO_CLIENTE = (('FIRMARA_DOCUMENTOS', 'Firmará Documentos'), 
                    ('DOCUMENTOS_FIRMADOS', 'Documentos Firmados'), 
                    ('RECHAZA_OFERTA', 'Rechaza Oferta'))

ESTADO_CURSE = (('NO_CURSADA', 'No Cursada'), 
                ('EN_PROCESO', "En Proceso"), 
                ('ENVIADA_A_CURSE', 'Enviada a Curse'))

ESTADO_DIARIO = (("MOROSO", "Moroso"),
                ("AL_DIA", "Al Día"))

OPCIONES_CANAL = ((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"))

OPCIONES_POSTERGACION = (("SI", "SI"), ("NO", "NO"))

OPCIONES_OFERTA = (("OFERTA_1", "Oferta 1"), ("OFERTA_2", "Oferta 2"))

class Cliente(models.Model):
    cli_rut = models.IntegerField(primary_key=True, help_text="Sin dígito verificador")
    cli_nom = models.CharField(max_length=100)

    impacto_gasto = models.IntegerField()

    tel_fijo_1 = models.IntegerField(blank=True, null = True,  help_text="+56 + (cod reg) + (num)")
    tel_fijo_2 = models.IntegerField(blank=True, null = True, help_text="+56 + (cod reg) + (num)")
    tel_cel_1 = models.IntegerField(blank=True, help_text="+569 + (123456789)")
    tel_cel_2 = models.IntegerField(blank=True, help_text="+569 + (123456789)")

    direccion_particular = models.CharField(max_length = 100, blank = True, null = True)
    direccion_comercial  = models.CharField(max_length = 100, blank = True, null = True)

    zona_cli = models.CharField(max_length = 30, 
                                        choices = ZONAS, 
                                        blank = False, 
                                        null = False)

    modulo_cli = models.CharField(max_length = 30, 
                                        choices = MODULOS_NORTE + MODULOS_CENTRO + MODULOS_SUR, 
                                        blank = False, 
                                        null = False)

    sucursal_cli = models.CharField(max_length = 50)

    ejecutivo_cartera = models.ForeignKey(EjecutivoComercial, on_delete = models.SET_NULL, null=True, related_name='pertenece_a_la_cartera', help_text="Sólo Ejecutivo")
    gestor  = models.ForeignKey(Persona, on_delete = models.SET_NULL, null=True, blank = True, related_name='actualmente_gestionando', help_text="Ejecutivos y Asistentes Comerciales")

    estado_diario = models.CharField(max_length = 50, 
                                        choices = ESTADO_DIARIO,
                                        blank = True, 
                                        null = True)


    postergacion  = models.CharField(max_length = 50, 
                                        choices = OPCIONES_POSTERGACION,
                                        blank = True, 
                                        null = True)

    preaprobados_reng    = models.BooleanField(verbose_name="Preaprobados Rene")


    canal_ccl     = models.IntegerField(choices = OPCIONES_CANAL,
                                        blank = True, 
                                        null = True, verbose_name="Canal CCL")

    canal_web     = models.BooleanField(null = True, verbose_name="Canal WEB")

    disponibilidad_oferta    = models.BooleanField(verbose_name="Disponibilidad de Ofertas")

    eleccion_oferta  = models.CharField(max_length = 50, 
                                        choices = OPCIONES_OFERTA,
                                        blank = True, 
                                        null = True)
    
    fecha_asignacion = models.DateField(null = True, blank=True)
    
    fecha_gestion    = models.DateField(null = True, blank=True) 
    

    contactabilidad = models.CharField(max_length = 50, 
                                        choices = CONTACTABILIDAD,
                                        blank = True, 
                                        null = True)

    respuesta_cliente  = models.CharField(max_length = 30, 
                                        choices = RESPUESTAS_CLIENTE, 
                                        blank = True, 
                                        null = True)
    
    estado = models.CharField(max_length = 30, 
                                        choices = ESTADO, 
                                        blank = True, 
                                        null = True)


    fecha_reinsistencia    = models.DateField(blank=True, 
                                                null = True) 

    contacto_cliente_interesado = models.CharField(max_length = 30, 
                                        choices = CONTACTO_CLIENTE_INTERESADO, 
                                        blank = True, 
                                        null = True)

    estado_cliente = models.CharField(max_length = 30, 
                                        choices = ESTADO_CLIENTE, 
                                        blank = True, 
                                        null = True)

    fecha_firma = models.DateField(blank=True, 
                                    null = True) 

    estado_curse = models.CharField(max_length = 30, 
                                        choices = ESTADO_CURSE,
                                        blank = True,
                                        null = True)

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
