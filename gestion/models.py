from django.db import models
from reclamations.models import Laboratoire, PC

# Modèle Salle
class Salle(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Modèle Bureau
class Bureau(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom