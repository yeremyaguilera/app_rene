# Generated by Django 2.2.10 on 2020-05-13 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0002_auto_20200512_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualizagestion',
            name='info_gestion',
            field=models.FileField(blank=True, help_text='Debe ser el archivo de gestión del ejecutivo', null=True, upload_to='gestiones/13-05-2020'),
        ),
    ]
