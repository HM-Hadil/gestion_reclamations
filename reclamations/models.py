from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Laboratoire(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Reclamation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    LIEU_CHOICES = [
        ('labo', 'Laboratoire'),
        ('salle', 'Salle'),
        ('bureau', 'Bureau'),
    ]

    description = models.TextField()
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    lieu = models.CharField(max_length=20, choices=LIEU_CHOICES)  # Choix du lieu : labo, salle, bureau
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Réclamation {self.lieu} de {self.user.email} - {self.statut}"

class ReclamationPC(models.Model):
    PROBLEME_TYPE_CHOICES = [
        ('materiel', 'Problème Matériel'),
        ('logiciel', 'Problème Logiciel'),
    ]

    MATERIEL_CHOICES = [
        ('clavier', 'Clavier'),
        ('souris', 'Souris'),
        ('ecran', 'Écran'),
        ('imprimante', 'Imprimante'),
        ('scanner', 'Scanner'),
        ('carte_reseau', 'Carte Réseau'),
    ]

    LOGICIEL_CHOICES = [
        ('connexion_internet', 'Connexion Internet'),
        ('systeme_exploitation', 'Système d\'Exploitation'),
        ('installation', 'Installation Logicielle'),
        ('antivirus', 'Antivirus'),
    ]

    reclamation = models.OneToOneField(Reclamation, on_delete=models.CASCADE, primary_key=True)
    type_probleme = models.CharField(max_length=20, choices=PROBLEME_TYPE_CHOICES)
    materiel = models.CharField(max_length=20, choices=MATERIEL_CHOICES, null=True, blank=True)
    logiciel = models.CharField(max_length=20, choices=LOGICIEL_CHOICES, null=True, blank=True)
    details_probleme = models.TextField()

    def __str__(self):
        return f"Réclamation PC - {self.type_probleme}"


class ReclamationElectrique(models.Model):
    PROBLEME_CHOICES = [
        ('climatiseur', 'Climatiseur'),
        ('coupure_courant', 'Coupure de Courant'),
    ]

    CLIMATISEUR_ETAT_CHOICES = [
        ('dysfonctionnement_partiel', 'Dysfonctionnement Partiel'),
        ('absence', 'Absence de Climatiseur'),
        ('panne', 'Panne Complète'),
    ]

    reclamation = models.OneToOneField(Reclamation, on_delete=models.CASCADE, primary_key=True)
    type_probleme = models.CharField(max_length=20, choices=PROBLEME_CHOICES)
    etat_climatiseur = models.CharField(max_length=30, choices=CLIMATISEUR_ETAT_CHOICES, null=True, blank=True)
    description_climatiseur = models.TextField(null=True, blank=True)
    description_coupure = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Réclamation Électrique - {self.type_probleme}"


class ReclamationDivers(models.Model):
    PROBLEME_CHOICES = [
        ('tableau_blanc', 'Tableau Blanc'),
        ('video_projecteur', 'Vidéo Projecteur'),
    ]

    ETAT_CHOICES = [
        ('dysfonctionnement_partiel', 'Dysfonctionnement Partiel'),
        ('absence', 'Absence'),
        ('panne', 'Panne Complète'),
    ]

    reclamation = models.OneToOneField(Reclamation, on_delete=models.CASCADE, primary_key=True)
    type_probleme = models.CharField(max_length=30, choices=PROBLEME_CHOICES)
    etat = models.CharField(max_length=30, choices=ETAT_CHOICES)
    description = models.TextField()

    def __str__(self):
        return f"Réclamation Divers - {self.type_probleme}"
