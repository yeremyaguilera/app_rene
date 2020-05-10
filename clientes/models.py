from django.db import models
import sys
sys.path.append("..")
from personas_beme.models import MODULOS_CENTRO, MODULOS_NORTE, MODULOS_SUR
from personas_beme.models import SUCURSALES_CENTRO, SUCURSALES_NORTE, SUCURSALES_SUR
from personas_beme.models import ZONAS

from personas_beme.models import EjecutivoComercial

# Create your models here.
CONTACTABILIDAD = (('CON_CONTACTO', 'Contactado'), 
                    ('SIN_CONTACTO', 'Sin Contacto'))

RESPUESTAS_CLIENTE = (("INTERESADO_EN_OFERTA", 'Interesado en Oferta Simulador'), 
                        ('INTERESADO_EN_RENEGOCIAR', 'Interesado en Renegociar - Derivar a la Plataforma BEME'), 
                        ('NO_INTERESADO-PAGARA_CUOTA', 'No Interesado - Pagará Cuota'))

ESTADO = (("SE_ACERCARA", "Se acercará a la Sucursal"),
                    ("NO_SE_ACERCARA", "No puede acercarse a la Sucursal"),
                    ("LO_PENSARA", "Lo Pensará"))

CONTACTO_CLIENTE_INTERESADO = (('AGENDADO', 'Agendado'), 
                                ('SIN_CONTACTO', "Sin Contacto"))

ESTADO_CLIENTE = (('FIMARA', 'Firmará Documentos'), 
                    ('DOCUMENTOS_FIRMADOS', 'Documentos Firmados'), 
                    ('RECHAZA_OFERTA', 'Rechaza Oferta'))

ESTADO_CURSE = (('NO_CURSADA', 'No Cursada'), 
                ('CURSADA', 'Cursada'), 
                ('EN_PROCESO', "En Proceso"))

class Cliente(models.Model):
    cli_rut = models.IntegerField(primary_key=True, help_text="Sin dígito verificador")
    cli_nom = models.CharField(max_length=100)

    ejecutivo_cartera = models.ForeignKey(EjecutivoComercial, on_delete = models.SET_NULL, null=True, related_name='pertenece_a_la_cartera')
    ejecutivo_gestor  = models.ForeignKey(EjecutivoComercial, on_delete = models.SET_NULL, null=True, related_name='actualmente_gestionando')


    zona_cli = models.CharField(max_length = 30, 
                                        choices = ZONAS, 
                                        blank = False, 
                                        null = False)

    modulo_cli = models.CharField(max_length = 30, 
                                        choices = MODULOS_NORTE + MODULOS_CENTRO + MODULOS_SUR, 
                                        blank = False, 
                                        null = False)


    sucursal_cli = models.CharField(max_length = 50)
    
    tel_fijo_1 = models.IntegerField(blank=True, null = True,  help_text="+56 + (cod reg) + (num)")
    tel_fijo_2 = models.IntegerField(blank=True, null = True, help_text="+56 + (cod reg) + (num)")
    tel_cel_1 = models.IntegerField(blank=True, help_text="+569 + (123456789)")
    tel_cel_2 = models.IntegerField(blank=True, help_text="+569 + (123456789)")

    direccion_particular = models.CharField(max_length = 100, blank = True, null = True)
    direccion_comercial  = models.CharField(max_length = 100, blank = True, null = True)

    impacto_gasto = models.IntegerField()

    fecha_asignacion = models.DateField(blank=True)
    fecha_gestion    = models.DateField(blank=True) 


    respuesta  = models.CharField(max_length = 30, 
                                        choices = RESPUESTAS_CLIENTE, 
                                        blank = True, null = True)
    
    fecha_reinsistencia    = models.DateField(blank=True) 

    estado_contacto_interesado = models.CharField(max_length = 30, 
                                        choices = CONTACTO_CLIENTE_INTERESADO, 
                                        blank = True, null = True)

    fecha_firma = models.DateField(blank=True) 

    estado_diario = models.CharField(max_length = 50, 
                                        choices = (("MOROSO", "Moroso"),
                                                    ("AL_DIA", "Al Día")),
                                        blank = True, 
                                        null = True)
    postergacion  = models.BooleanField()
    canal_ccl     = models.BooleanField(verbose_name="Canal CCL")
    canal_web     = models.BooleanField(verbose_name="Canal WEB")

    def __str__(self):
        return self.cli_nom +': '+ str(self.cli_rut)

class OfertaCliente(models.Model):
    class Meta:
        verbose_name = "Oferta Cliente"
        verbose_name_plural = "Ofertas Clientes"
        unique_together = ("fecha_de_oferta", "cliente")

    cliente           = models.ForeignKey(Cliente, on_delete = models.DO_NOTHING, related_name='cliente')
    
    fecha_de_oferta   = models.DateField(null=False, blank=False)

    ope_tasa_oferta_1       = models.FloatField(default = 0, blank=False)
    plazo_oferta_1          = models.IntegerField(default = 1, blank=False)
    monto_oferta_1          = models.IntegerField(default = 0, blank=False)
    per_rebaja_oferta_1     = models.FloatField(default = 0, blank=False)
    total_a_pagar_oferta_1  = models.IntegerField(default = 0, blank=False)

    ope_tasa_oferta_2       = models.FloatField(default = 0, blank=False)
    plazo_oferta_2          = models.IntegerField(default = 1, blank=False)
    monto_oferta_2          = models.IntegerField(default = 0, blank=False)
    per_rebaja_oferta_2     = models.FloatField(default = 0, blank=False)
    total_a_pagar_oferta_2  = models.IntegerField(default = 0, blank=False)

    def __str__(self):
        return self.cliente.__str__() + ': '+ str(self.fecha_de_oferta)
