# Generated by Django 2.2.10 on 2020-05-11 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0007_auto_20200510_2119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ofertacliente',
            name='eleccion_oferta',
        ),
        migrations.AddField(
            model_name='cliente',
            name='eleccion_oferta',
            field=models.CharField(blank=True, choices=[('OFERTA_1', 'Oferta 1'), ('OFERTA_2', 'Oferta 2')], max_length=50, null=True),
        ),
    ]