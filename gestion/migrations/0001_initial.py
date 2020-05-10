# Generated by Django 2.2.10 on 2020-04-29 03:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('personas_beme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contraparte',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ejecutivo_contraparte', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ejecutivo_contraparte', to='personas_beme.EjecutivoComercial')),
                ('ejecutivo_sin_acceso', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ejecutivo_sin_acceso', to='personas_beme.EjecutivoComercial')),
            ],
            options={
                'verbose_name': 'Contrapartes',
                'verbose_name_plural': 'Contrapartes',
            },
        ),
        migrations.CreateModel(
            name='ActualizaGestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('info_gestion', models.FileField(blank=True, help_text='Debe ser el archivo de gestión del ejecutivo', null=True, upload_to='gestiones/')),
                ('ejecutivo', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ejecutivo', to='personas_beme.EjecutivoComercial')),
            ],
            options={
                'verbose_name': 'Actualizador de Gestión',
                'verbose_name_plural': 'Actualizados de Gestión',
            },
        ),
    ]