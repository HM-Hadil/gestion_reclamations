# Generated by Django 5.2 on 2025-05-22 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_alter_pc_ecran_alter_pc_logiciels_installes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salle',
            name='memoire_ram',
        ),
        migrations.RemoveField(
            model_name='salle',
            name='modele_postes',
        ),
        migrations.RemoveField(
            model_name='salle',
            name='processeur',
        ),
        migrations.RemoveField(
            model_name='salle',
            name='stockage',
        ),
        migrations.DeleteModel(
            name='PC',
        ),
    ]
