# Generated by Django 2.2.10 on 2020-05-15 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personas_beme', '0002_auto_20200515_1114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='persona',
            old_name='codigo_ejecutivo',
            new_name='codigo_persona_beme',
        ),
    ]
