# gestion/serializers.py
from rest_framework import serializers
# Import models from the same app (gestion)
from .models import PC, Salle, Laboratoire, Bureau


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = '__all__'


class PCSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        # Inclure laboratoire pour pouvoir voir à quel labo le PC est rattaché
        fields = ['id', 'poste', 'sn_inventaire', 'logiciels_installes', 'ecran', 'laboratoire']


class LaboratoireSerializer(serializers.ModelSerializer):
    # Serializer imbriqué pour afficher les PCs rattachés à un laboratoire
    pcs = PCSerializer(many=True, read_only=True)

    class Meta:
        model = Laboratoire
        # Inclure 'pcs' pour afficher les PCs lors de la récupération d'un laboratoire
        fields = ['id', 'nom', 'modele_postes', 'processeur', 'memoire_ram', 'stockage', 'pcs']


class BureauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bureau
        fields = '__all__'