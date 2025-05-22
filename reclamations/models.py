from django.db import models
from django.conf import settings

class Laboratoire(models.Model):
    nom = models.CharField(max_length=100)
    modele_postes = models.CharField(max_length=200, verbose_name="Modèle des postes", blank=True)
    processeur = models.CharField(max_length=200, verbose_name="Processeur", blank=True)
    memoire_ram = models.CharField(max_length=100, verbose_name="Mémoire RAM", blank=True)
    stockage = models.CharField(max_length=100, verbose_name="Stockage", blank=True)
    
    def __str__(self):
        return self.nom

class PC(models.Model):
    poste = models.CharField(max_length=255, unique=True, verbose_name="Poste")
    sn_inventaire = models.CharField(max_length=100, unique=True, verbose_name="S/N Inventaire")
    logiciels_installes = models.TextField(verbose_name="Logiciels Installés", blank=True)
    ecran = models.CharField(max_length=255, verbose_name="Écran", blank=True)
    laboratoire = models.ForeignKey(
        Laboratoire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pcs',
        verbose_name="Laboratoire"
    )
    
    def __str__(self):
        return f"PC {self.poste} - {self.sn_inventaire}"
    
    class Meta:
        verbose_name = "PC"
        verbose_name_plural = "PCs"
        db_table = 'gestion_pc'  # Utilise la table existante

# Suppression du modèle Equipement - on utilise directement PC
# class Equipement(models.Model): # SUPPRIMÉ

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

    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
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
    # Remplacer equipement par pc
    pc = models.ForeignKey(
        PC, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reclamations'
    )
    category = models.CharField(
        max_length=10, 
        choices=CATEGORY_CHOICES, 
        verbose_name='Catégorie',
        null=True,  
        blank=True  
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente',
        verbose_name='Statut'
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