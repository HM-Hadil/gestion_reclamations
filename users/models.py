from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re

def validate_isimg_email(value):
    """ Vérifie que l'email suit le format nom.prenom@isimg.tn """
    email_pattern = r'^[a-zA-Z]+\.[a-zA-Z]+@isimg\.tn$'
    if not re.match(email_pattern, value):
        raise ValidationError("Seuls les emails au format 'nom.prenom@isimg.tn' sont autorisés.")

class User(AbstractUser):
    ROLE_CHOICES = [
        ('responsable', 'Responsable'),
        ('technicien', 'Technicien'),
        ('enseignant', 'Enseignant'),
    ]

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, validators=[validate_isimg_email])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,
    default='enseignant', blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)  # Ajout du champ image

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role']

    def __str__(self):
        return self.email
