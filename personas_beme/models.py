from django.db import models


# Create your models here.
STATUS_PERSONAS = (("CASA_SIN_VDI", "En casa sin acceso remoto"),
                    ("CASA_CON_VDI", "En casa con acceso remoto"),
                    ("EN_SUCURSAL", "En Sucursal"))

CARGOS = (("ASESOR_COMERCIAL", "Asesor Comercial de Riesgo"), 
            ("EJECUTIVO_COMERCIAL", "Ejecutivo Comercial"),
            ("ASISTENTE_COMERCIAL", "Asistente Comercial"))

ZONAS = (('ZONA_NORTE' , 'Zona Norte'),
        ('ZONA_CENTRO', 'Zona Centro'),
        ('ZONA_SUR'   , 'Zona Sur'))

MODULOS_NORTE = (('XV_REGION'      , 'NORTE: XV Región'),
            ('I_REGION'            , 'NORTE: I Región'),
            ('II_REGION'           , 'NORTE: II Región'),
            ('III_REGION'          , 'NORTE: III Región'),
            ('IV_REGION'           , 'NORTE: IV Región'),
            ('V_REGION_COSTA'      , 'NORTE: V Región Costa'),
            ('V_REGION_CORDILLERA' , 'NORTE: V Región Cordillera'),
            ('VI_REGION'           , 'NORTE: VI Región'))

MODULOS_CENTRO = (('METROPOLITANA_PONIENTE', 'CENTRO: Metropolitana Poniente'),
            ('METROPOLITANA_ORIENTE'       , 'CENTRO: Metropolitana Oriente'),
            ('METROPOLITANA_SUR'           , 'CENTRO: Metropolitana Sur'),
            ('METROPOLITANA_CENTRO'        , 'CENTRO: Metropolitana Centro'),
            ('METROPOLITANA_NORTE'         , 'CENTRO: Metropolitana Norte'))

MODULOS_SUR = (('VII_REGION'          , 'SUR: VII Región'),
            ('BIOBIO_NORTE'           , 'SUR: Bío Bío Norte'),
            ('BIOBIO_SUR'             , 'SUR: Bío Bío Sur'),
            ('VIII_REGION_CORDILLERA' , 'SUR: VIII Región Cordillera'),
            ('IX_REGION_NORTE'        , 'SUR: IX Región Norte'),
            ('IX_REGION_SUR'          , 'SUR: IX Región Sur'),
            ('XIV_REGION'             , 'SUR: XIV Región'),
            ('X_REGION'               , 'SUR: X Región'),
            ('XI_REGION'              , 'SUR: XI Región'),
            ('XII_REGION'             , 'SUR: XII Región'))

SUCURSALES_NORTE = (('SUBGERENCIA_REGIONAL_XV_REGION', 'NORTE: Subgerencia Regional XV Región'),
                    ('ARICA', 'NORTE: Arica'),
                    ('ARICA_SANTA_MARIA', 'NORTE: Arica Santa María'))


SUCURSALES_CENTRO = (('SUBGERENCIA_REGIONAL_RM_CENTRO', 'CENTRO: Subgerencial Regional RM Centro'),
                ('DIEZ_DE_JULIO'              , 'CENTRO: Diez de Julio'),
                ('SANTIAGO_PRINCIPAL'         , 'CENTRO: Santiago Principal'),
                ('SANTIAGO_JOSE_MARIA_CARO'   , 'CENTRO: Santiago José María Caro'),
                ('MATUCANA'                   , 'CENTRO: Matucana'),
                ('ESTACION_CENTRAL'           , 'CENTRO: Estación Central'),
                ('SANTIAGO_SAN_DIEGO'         , 'CENTRO: Santiago San Diego'),
                ('PASEO_HUERFANOS'            , 'CENTRO: Paseo Huerfanos'),
                ('SANTIAGO_SERVIESTADO'       , 'CENTRO: Santiago ServiEstado'),
                ('SANTIAGO_LA_LEGUA'          , 'CENTRO: Santiago La Legua'),
                ('SANTA_LUCIA'                , 'CENTRO: Santa Lucía'),
                ('AVENIDA_MATTA'              , 'CENTRO: Avenida Matta'),
                ('BANDERA'                    , 'CENTRO: Bandera'),
                ('PASEO_ESTADO'               , 'CENTRO: Paseo Estado'),
                ('VICUÑA_MACKENNA'            , 'CENTRO: Vicuña Mackenna'),
                ('SANTA_ANA'                  , 'CENTRO: Santa Ana'),
                ('CENTRO_DE_ATENCION_DIGITAL' , 'CENTRO: Centro de Atención Digital La Moneda'),
                ('LO_ESPEJO'                  , 'CENTRO: Lo Espejo'),
                ('PLATAFORMA_REMOTA'          , 'CENTRO: Plataforma Remota Microempresas'))

SUCURSALES_SUR = (('SUBGERENCIA_REGIONAL_VII_REGION', 'SUR: Subgerencia Regional VII Región'),
                    ('TALCA'                        , 'SUR: Talca'),
                    ('LINARES'                      , 'SUR: LINARES'))

class Persona(models.Model):
    codigo_persona_beme = models.CharField(max_length = 50, primary_key=True)
    nombre              = models.CharField(max_length = 50)
    apellido            = models.CharField(max_length = 50)
    apellido_materno    = models.CharField(max_length = 50)
    email               = models.EmailField()

    cargo = models.CharField(max_length = 30, 
                                        choices = CARGOS, 
                                        blank = False, 
                                        null = False)

    zona = models.CharField(max_length = 15, 
                                        choices = ZONAS, 
                                        blank = False, 
                                        null = False)

    modulo = models.CharField(max_length = 30, 
                                        choices = MODULOS_NORTE + MODULOS_CENTRO + MODULOS_SUR, 
                                        blank = False, 
                                        null = False)


    sucursal = models.CharField(max_length = 50)

    status = models.CharField(max_length = 20, 
                                        choices = STATUS_PERSONAS, 
                                        blank = False, 
                                        null = False)


    def __str__(self):
        return self.cargo +': '+ str(self.nombre) + " " + str(self.apellido)

    
class AsesorManager(models.Manager):
    def get_queryset(self):
        return super(AsesorManager, self).get_queryset().filter(cargo="ASESOR_COMERCIAL")

class Asesor(Persona):
    objects = AsesorManager()
    class Meta:
        proxy = True
        verbose_name = "Asesor"
        verbose_name_plural = "Asesores"
    
    def __str__(self):
        return self.nombre + ' '+ str(self.apellido) + ' ' + self.apellido_materno

class EjecutivoComercialManager(models.Manager):

    def get_queryset(self):
        return super(EjecutivoComercialManager, self).get_queryset().filter(cargo="EJECUTIVO_COMERCIAL")


class EjecutivoComercial(Persona):
    objects = EjecutivoComercialManager()
    class Meta:
        proxy = True
        verbose_name = "Ejecutivo Comercial"
        verbose_name_plural = "Ejecutivos Comerciales"

    def __str__(self):
        return self.nombre + ' '+ str(self.apellido) + ' ' + self.apellido_materno


class AsistenteComercialManager(models.Manager):
    def get_queryset(self):
        return super(AsistenteComercialManager, self).get_queryset().filter(cargo="ASISTENTE_COMERCIAL")

class AsistenteComercial(Persona):
    objects = AsistenteComercialManager()
    class Meta:
        proxy = True
        verbose_name = "Asistente Comercial"
        verbose_name_plural = "Asistentes Comerciales"

    def __str__(self):
        return self.nombre + ' '+ str(self.apellido) + ' ' + self.apellido_materno


