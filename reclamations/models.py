from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Reclamation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    TYPE_CHOICES = [
        ('pc', 'PC'),
        ('materiel', 'Matériel'),
        ('equipement', 'Équipement'),
    ]

    description = models.TextField()
    date_soumission = models.DateTimeField(auto_now_add=True)  # Date auto lors de la création
    date_modification = models.DateTimeField(auto_now=True)  # Mise à jour auto à chaque modification
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    type_reclamation = models.CharField(max_length=20, choices=TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Lien avec l'utilisateur qui crée la réclamation

    def __str__(self):
        return f"Réclamation de {self.user.email} - {self.statut}"
