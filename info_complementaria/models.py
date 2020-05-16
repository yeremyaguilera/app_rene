from django.db import models
# Create your models here.

class UF(models.Model):
    class Meta:
        verbose_name = "UF"
        verbose_name_plural = "UF"
    dia      = models.DateField(null=False, blank=False) 
    valor_uf = models.DecimalField(max_digits=7, decimal_places=2)
    def __str__(self):
        return str(self.valor_uf) + ' : ' + str(self.dia)


RANGOS = (("[1  , 12]" , "[1  , 12]"),
          ("[13 , 24]" , "[13 , 24]"),
          ("[25 , 36]" , "[25 , 36]"),
          ("[37 , 48]" , "[37 , 48]"),
          ("[49 , 60]" , "[49 , 60]"),
          ("[61 , 72]" , "[61 , 72]"),
          ("[73 , 84]" , "[73 , 84]"),
          ("[85 , 96]" , "[85 , 96]"),
          ("[97 , 108]", "[97 , 108]"),
          ("[109, 120]", "[109, 120]"))

class TasaSeguro(models.Model):
    class Meta:
        verbose_name = "Tasa Seguro"
        verbose_name_plural = "Tasas Seguro"

    plazo = models.CharField(max_length = 30, 
                                        choices = RANGOS, 
                                        blank = False, 
                                        null = False)
                        
    valor_tasa = models.DecimalField(max_digits=7, decimal_places=6, default=0)

    def __str__(self):
        return "Plazo : " + str(self.plazo) + ' : ' + str(self.valor_tasa) + "%"
    
class PeriodoGracia(models.Model):

    periodo_de_gracia = models.IntegerField(default = 0, blank=False)

    class Meta:
        verbose_name = "Periodo de Gracia"
        verbose_name_plural = "Periodos de Gracia"

    def __str__(self):
        return 'Periodo de Gracia :' + str(self.periodo_de_gracia) + ' Meses'


class TasaOferta(models.Model):

    ope_tasa = models.FloatField(default = 0, blank=False, help_text="Debe estar en porcentaje %")

    class Meta:
        verbose_name = "Tasa de Oferta"
        verbose_name_plural = "Tasas de Oferta"

    def __str__(self):
        return 'Tasa Oferta : ' + str(self.ope_tasa) + ' %'

