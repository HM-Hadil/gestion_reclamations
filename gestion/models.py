from django.db import models

from reclamations.models import Laboratoire

# Modèle Salle
class Salle(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Modèle Laboratoireclass Laboratoire(models.Model):
    nom = models.CharField(max_length=100)
    modele_postes = models.CharField(max_length=200, verbose_name="Modèle des postes", blank=True)
    processeur = models.CharField(max_length=200, verbose_name="Processeur", blank=True)
    memoire_ram = models.CharField(max_length=100, verbose_name="Mémoire RAM", blank=True)
    stockage = models.CharField(max_length=100, verbose_name="Stockage", blank=True)
    
    def __str__(self):
        return self.nom


# Modèle Bureau
class Bureau(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Modèle PC
# Modèle PC
class PC(models.Model):
    # Post string: un identifiant ou un nom pour le PC
    poste = models.CharField(max_length=255, unique=True, verbose_name="Poste")

    # Numéro de série de l'inventaire
    sn_inventaire = models.CharField(max_length=100, unique=True, verbose_name="S/N Inventaire")

    # Liste des logiciels installés - peut être un champ de type texte
    logiciels_installes = models.TextField(verbose_name="Logiciels Installés", blank=True) # Added blank=True, often software list can be empty

    # Description de l'écran (peut inclure la taille, la résolution, etc.)
    ecran = models.CharField(max_length=255, verbose_name="Écran", blank=True) # Added blank=True

    # Ajout de la relation avec le laboratoire (ForeignKey)
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
    def __str__(self):
        return f"PC {self.poste} - {self.sn_inventaire}"
