from django.db import models

class Salle(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Laboratoire(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Bureau(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
