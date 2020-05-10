from django.contrib import admin

from .models import UF, TasaSeguro
# Register your models here.

@admin.register(UF)
class UFAdmin(admin.ModelAdmin):

    list_display_links = ('dia',)

    fields = ('dia', 'valor_uf')
    list_display = fields

@admin.register(TasaSeguro)
class TasaSeguroAdmin(admin.ModelAdmin):

    list_display_links = ('plazo',)

    fields = ('plazo', 'valor_tasa')
    list_display = fields