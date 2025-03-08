from rest_framework import serializers
from .models import Reclamation

class ReclamationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reclamation
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}  # On empêche l'utilisateur de fournir ce champ
        }