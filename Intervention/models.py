from django.db import models

from gestion_reclamations import settings
from reclamations.models import Reclamation
class Intervention(models.Model):
    """Modèle pour gérer les interventions sur les réclamations"""
    reclamation = models.ForeignKey(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='interventions'
    )
    technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interventions_assignees'
    )
    description = models.TextField(blank=True, null=True)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    
    ACTION_CHOICES = [
        ('diagnostique', 'Diagnostique'),
        ('reparation', 'Réparation'),
        ('remplacement', 'Remplacement'),
        ('autre', 'Autre')
    ]
    action_effectuee = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"Intervention #{self.id} - Réclamation #{self.reclamation.id}"
    
    def terminer(self):
        """Marquer l'intervention comme terminée"""
        from django.utils import timezone
        self.date_fin = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la réclamation
        self.reclamation.status = 'termine'
        self.reclamation.save()