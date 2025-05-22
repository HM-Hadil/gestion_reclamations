# interventions/models.py
from django.db import models
from gestion_reclamations import settings
from reclamations.models import Reclamation
class Intervention(models.Model):
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

    probleme_constate = models.TextField(blank=True, null=True,
        help_text="Description détaillée du problème constaté lors de l'intervention")
    analyse_cause = models.TextField(blank=True, null=True,
        help_text="Analyse et cause identifiée du problème")
    actions_entreprises = models.TextField(blank=True, null=True,
        help_text="Actions entreprises pour résoudre le problème")
    pieces_remplacees = models.TextField(blank=True, null=True,
        help_text="Liste des pièces remplacées pendant l'intervention")
    resultat_tests = models.TextField(blank=True, null=True,
        help_text="Résultats des tests effectués après l'intervention")
    recommandations = models.TextField(blank=True, null=True,
        help_text="Recommandations pour éviter que le problème ne se reproduise")
    mots_cles = models.CharField(max_length=255, blank=True, null=True,
        help_text="Mots-clés pour faciliter la recherche d'interventions similaires")
    fichier_joint = models.FileField(upload_to='interventions/fichiers/', blank=True, null=True,
        help_text="Fichier joint à l'intervention (photos, diagnostics, etc.)")
    rapport_pdf = models.FileField(upload_to='interventions/rapports/', blank=True, null=True,
        help_text="Rapport PDF généré de l'intervention")

    def __str__(self):
        return f"Intervention #{self.id} - Réclamation #{self.reclamation.id}"

    def terminer(self):
        from django.utils import timezone
        self.date_fin = timezone.now()
        self.save()
        self.reclamation.status = 'termine'
        self.reclamation.save()