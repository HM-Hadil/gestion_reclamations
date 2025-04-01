from django.db import models
from django.conf import settings

class Laboratoire(models.Model):
    """Représente un laboratoire spécifique"""
    nom = models.CharField(max_length=100, unique=True, verbose_name='Nom du Laboratoire')
    
    def __str__(self):
        return self.nom

class Equipement(models.Model):
    """Modèle pour gérer les équipements dans un laboratoire"""
    laboratoire = models.ForeignKey(
        Laboratoire, 
        on_delete=models.CASCADE, 
        related_name='equipements'
    )
    TYPE_CHOICES = [
        ('pc', 'Ordinateur'),
        ('electrique', 'Équipement Électrique'),
        ('divers', 'Équipement Divers')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    identificateur = models.CharField(max_length=50, verbose_name="Identifiant de l'équipement")  # Fixed here
    
    def __str__(self):
        return f"{self.identificateur} - {self.get_type_display()} ({self.laboratoire.nom})"

class Reclamation(models.Model):
    """Modèle principal pour les réclamations"""
    LIEU_CHOICES = [
        ('labo', 'Laboratoire'),
        ('salle', 'Salle'),
        ('bureau', 'Bureau')
    ]

    CATEGORY_CHOICES = [
        ('pc', 'Problèmes PC'),
        ('electrique', 'Problèmes Électriques'),
        ('divers', 'Problèmes Divers')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations'
    )
    lieu = models.CharField(max_length=10, choices=LIEU_CHOICES)
    laboratoire = models.ForeignKey(
        Laboratoire, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    equipement = models.ForeignKey(
        Equipement, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    category = models.CharField(
        max_length=10, 
        choices=CATEGORY_CHOICES, 
        verbose_name='Catégorie',
        null=True,  
        blank=True  
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    description_generale = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Description générale'
    )
    
    def __str__(self):
        return f"Réclamation {self.id} - {self.get_lieu_display()} - {self.get_category_display() if self.category else 'Sans Catégorie'}"

class ReclamationPC(models.Model):
    """Détails pour les réclamations liées aux ordinateurs"""
    reclamation = models.OneToOneField(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='pc_details'
    )
    type_probleme = models.CharField(
        max_length=20, 
        choices=[('materiel', 'Problème Matériel'), ('logiciel', 'Problème Logiciel')]
    )
    description_probleme = models.TextField(null=True, blank=True)

class ReclamationElectrique(models.Model):
    """Détails pour les réclamations électriques"""
    reclamation = models.OneToOneField(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='electrique_details'
    )
    type_probleme = models.CharField(
        max_length=20, 
        choices=[('climatiseur', 'Climatiseur'), ('coupure_courant', 'Coupure de Courant'), ('autre', 'Autre')]
    )
    description_probleme = models.TextField(null=True, blank=True)

class ReclamationDivers(models.Model):
    """Détails pour les réclamations diverses"""
    reclamation = models.OneToOneField(
        Reclamation,
        on_delete=models.CASCADE,
        related_name='divers_details'
    )
    type_probleme = models.CharField(
        max_length=30, 
        choices=[('tableau_blanc', 'Tableau Blanc'), ('video_projecteur', 'Vidéo Projecteur'), ('autre', 'Autre')]
    )
    description_probleme = models.TextField(null=True, blank=True)
