from django.db import models
from personas_beme.models import Persona
import datetime
import os

from reneapp.settings import BASE_DIR


today_srt = datetime.datetime.today().date().strftime("%d-%m-%Y")
# Create your models here.
class Contraparte(models.Model):
    class Meta:
        verbose_name = "Contrapartes"
        verbose_name_plural = "Contrapartes"
        
        unique_together = ("gestor_sin_acceso", "contraparte")

    gestor_sin_acceso  = models.ForeignKey(Persona, null=True, on_delete= models.SET_NULL, related_name='gestor_sin_acceso')
    contraparte        = models.ForeignKey(Persona, null=True, on_delete= models.SET_NULL, related_name='contraparte')

    def __str__(self):
        return str(self.contraparte)

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    ruta_archivo = os.path.join(BASE_DIR, 'excel_files', 'distribucion_de_gestion', 'gestiones_realizadas', today_srt, instance.gestor.codigo_persona_beme, filename)
    return ruta_archivo


class ActualizaGestion(models.Model):
    class Meta:
        verbose_name = "Actualizador de Gestión"
        verbose_name_plural = "Actualizados de Gestión"

    gestor = models.ForeignKey(Persona, null=True,  on_delete= models.SET_NULL, related_name='Gestor')
    fecha  = models.DateField(auto_now_add=True, blank=True) 

    info_gestion = models.FileField(max_length=500, upload_to=user_directory_path, blank = True, null=True, help_text="Debe ser el archivo de gestión")

    def __str__(self):
        return str(self.gestor) + ' : '+ str(self.fecha)

