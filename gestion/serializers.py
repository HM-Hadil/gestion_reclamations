from rest_framework import serializers
from gestion.models import PC, Salle, Laboratoire, Bureau
from reclamations.models import Laboratoire


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = '__all__'  # Cela inclut tous les champs du modèle Salle
class PCSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ['id', 'poste', 'sn_inventaire', 'logiciels_installes', 'ecran', 'laboratoire']
class LaboratoireSerializer(serializers.ModelSerializer):
    pcs = PCSerializer(many=True, read_only=True)
    
    class Meta:
        model = Laboratoire
        fields = ['id', 'nom', 'modele_postes', 'processeur', 'memoire_ram', 'stockage', 'pcs']

class BureauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bureau
        fields = '__all__'  # Cela inclut tous les champs du modèle Bureau
