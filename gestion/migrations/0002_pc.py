# Generated by Django 4.2.19 on 2025-03-27 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poste', models.CharField(max_length=255, unique=True, verbose_name='Poste')),
                ('sn_inventaire', models.CharField(max_length=100, unique=True, verbose_name='S/N Inventaire')),
                ('logiciels_installes', models.TextField(verbose_name='Logiciels Installés')),
                ('ecran', models.CharField(max_length=255, verbose_name='Écran')),
            ],
            options={
                'verbose_name': 'PC',
                'verbose_name_plural': 'PCs',
            },
        ),
    ]
