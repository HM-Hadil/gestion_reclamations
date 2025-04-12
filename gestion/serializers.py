from rest_framework import serializers
from .models import PC, Salle, Laboratoire, Bureau

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
        fields = '__all__'

class BureauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bureau
        fields = '__all__'  # Cela inclut tous les champs du modèle Bureau
