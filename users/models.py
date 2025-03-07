from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re

class User(AbstractUser):
    ROLE_CHOICES = [
        ('responsable', 'Responsable'),
        ('technicien', 'Technicien'),
        ('enseignant', 'Enseignant'),
    ]
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role']

    def clean(self):
        super().clean()
        email_pattern = r'^[a-zA-Z]+\.[a-zA-Z]+@isimg\.tn$'
        if not re.match(email_pattern, self.email):
            raise ValidationError({'email': "Seuls les emails au format 'firstname.lastname@isimg.tn' sont autorisés."})

    def __str__(self):
        return self.email
