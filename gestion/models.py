from django.db import models
from personas_beme.models import EjecutivoComercial
import datetime


today_srt = datetime.datetime.today().date().strftime("%d-%m-%Y")
# Create your models here.
class Contraparte(models.Model):
    class Meta:
        verbose_name = "Contrapartes"
        verbose_name_plural = "Contrapartes"

    ejecutivo_sin_acceso  = models.ForeignKey(EjecutivoComercial, on_delete= models.DO_NOTHING, related_name='ejecutivo_sin_acceso')
    ejecutivo_contraparte = models.ForeignKey(EjecutivoComercial, on_delete= models.DO_NOTHING, related_name='ejecutivo_contraparte')

    def __str__(self):
        return str(self.ejecutivo_contraparte)

class ActualizaGestion(models.Model):
    class Meta:
        verbose_name = "Actualizador de Gestión"
        verbose_name_plural = "Actualizados de Gestión"

    ejecutivo = models.ForeignKey(EjecutivoComercial, on_delete= models.DO_NOTHING, related_name='ejecutivo')
    fecha     = models.DateField(auto_now_add=True, blank=True) 

    info_gestion = models.FileField(upload_to='gestiones/'+ today_srt, blank = True, null=True, help_text="Debe ser el archivo de gestión del ejecutivo")

    def __str__(self):
        return str(self.ejecutivo) + ' : '+ str(self.fecha)

