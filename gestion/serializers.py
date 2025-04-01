from rest_framework import serializers
from .models import PC, Salle, Laboratoire, Bureau

class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = '__all__'  # Cela inclut tous les champs du modèle Salle

class LaboratoireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratoire
        fields = '__all__'  # Cela inclut tous les champs du modèle Laboratoire

class BureauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bureau
        fields = '__all__'  # Cela inclut tous les champs du modèle Bureau
class PCSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ['id', 'poste', 'sn_inventaire', 'logiciels_installes', 'ecran']