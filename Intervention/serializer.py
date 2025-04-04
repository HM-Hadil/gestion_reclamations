from rest_framework import serializers
from .models import Intervention, Reclamation

class InterventionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Intervention
    """
    reclamation_details = serializers.SerializerMethodField()
    technicien_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Intervention
        fields = '__all__'
        read_only_fields = ['date_debut', 'date_fin']
    
    def get_reclamation_details(self, obj):
        """Retourne les détails de la réclamation liée"""
        return {
            'id': obj.reclamation.id,
            'category': obj.reclamation.get_category_display(),
            'lieu': obj.reclamation.get_lieu_display(),
            'laboratoire': obj.reclamation.laboratoire.nom if obj.reclamation.laboratoire else None,
            'description_generale': obj.reclamation.description_generale,
            'date_creation': obj.reclamation.date_creation
        }
    
    def get_technicien_nom(self, obj):
        """Retourne le nom complet du technicien"""
        return f"{obj.technicien.first_name} {obj.technicien.last_name}"
    
    def validate(self, data):
        """Validation personnalisée"""
        # Vérifier que la réclamation n'est pas déjà terminée
        reclamation = data.get('reclamation')
        if reclamation.status == 'termine':
            raise serializers.ValidationError("Cette réclamation est déjà terminée")
        
        return data

class RapportInterventionSerializer(serializers.Serializer):
    """
    Serializer pour générer un rapport d'intervention à partir d'une intervention existante
    """
    intervention_id = serializers.IntegerField()
    
    def validate_intervention_id(self, value):
        """Vérifier que l'intervention existe"""
        try:
            return Intervention.objects.get(id=value)
        except Intervention.DoesNotExist:
            raise serializers.ValidationError("Cette intervention n'existe pas")