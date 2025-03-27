from rest_framework import serializers
from .models import Reclamation, ReclamationPC, ReclamationElectrique, ReclamationDivers

class ReclamationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reclamation
        fields = '__all__'


class ReclamationPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReclamationPC
        fields = '__all__'


class ReclamationElectriqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReclamationElectrique
        fields = '__all__'


class ReclamationDiversSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReclamationDivers
        fields = '__all__'
