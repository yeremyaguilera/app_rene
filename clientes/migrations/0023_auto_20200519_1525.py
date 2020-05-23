# Generated by Django 2.2.10 on 2020-05-19 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0022_auto_20200518_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='disponibilidad_oferta',
            field=models.BooleanField(default=True, verbose_name='Disponibilidad de Oferta'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='ejecutivo_cartera',
            field=models.ForeignKey(help_text='Sólo Ejecutivo', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pertenece_a_la_cartera', to='personas_beme.EjecutivoComercial'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='gestor',
            field=models.ForeignKey(blank=True, help_text='Ejecutivos y Asistentes Comerciales', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actualmente_gestionando', to='personas_beme.Persona'),
        ),
    ]
