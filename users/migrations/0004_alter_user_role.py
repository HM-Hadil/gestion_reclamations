# Generated by Django 4.2.19 on 2025-04-12 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('responsable', 'Responsable'), ('technicien', 'Technicien'), ('enseignant', 'Enseignant')], default='enseignant', max_length=20),
        ),
    ]
