from django.db import models

# Modèle Salle
class Salle(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Modèle Laboratoire
class Laboratoire(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Modèle Bureau
class Bureau(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Modèle PC
class PC(models.Model):
    # Post string: un identifiant ou un nom pour le PC
    poste = models.CharField(max_length=255, unique=True, verbose_name="Poste")
    
    # Numéro de série de l'inventaire
    sn_inventaire = models.CharField(max_length=100, unique=True, verbose_name="S/N Inventaire")
    
    # Liste des logiciels installés - peut être un champ de type texte
    logiciels_installes = models.TextField(verbose_name="Logiciels Installés")
    
    # Description de l'écran (peut inclure la taille, la résolution, etc.)
    ecran = models.CharField(max_length=255, verbose_name="Écran")

    def __str__(self):
        return f"PC {self.poste} - {self.sn_inventaire}"

    class Meta:
        verbose_name = "PC"
        verbose_name_plural = "PCs"
