from rest_framework import serializers
from .models import Intervention
from reclamations.models import Reclamation
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
        reclamation = obj.reclamation
        
        # Données de base
        details = {
            'id': reclamation.id,
            'category': reclamation.get_category_display(),
            'lieu': reclamation.get_lieu_display(),
            'laboratoire': reclamation.laboratoire.nom if reclamation.laboratoire else None,
            'description_generale': reclamation.description_generale,
            'date_creation': reclamation.date_creation,
            'status': reclamation.get_status_display()
        }
        
        # Ajouter les détails spécifiques selon la catégorie
        if reclamation.category == 'pc' and hasattr(reclamation, 'pc_details'):
            details['details_specifiques'] = {
                'type_probleme': reclamation.pc_details.type_probleme,
                'description_probleme': reclamation.pc_details.description_probleme
            }
        elif reclamation.category == 'electrique' and hasattr(reclamation, 'electrique_details'):
            details['details_specifiques'] = {
                'type_probleme': reclamation.electrique_details.type_probleme,
                'description_probleme': reclamation.electrique_details.description_probleme
            }
        elif reclamation.category == 'divers' and hasattr(reclamation, 'divers_details'):
            details['details_specifiques'] = {
                'type_probleme': reclamation.divers_details.type_probleme,
                'description_probleme': reclamation.divers_details.description_probleme
            }
            
        return details
    
    def get_technicien_nom(self, obj):
        """Retourne le nom complet du technicien"""
        return f"{obj.technicien.first_name} {obj.technicien.last_name}"
    
    def validate(self, data):
        """Validation personnalisée"""
        # Vérifier que la réclamation n'est pas déjà terminée
        reclamation = data.get('reclamation')
        if reclamation and reclamation.status == 'termine':
            raise serializers.ValidationError("Cette réclamation est déjà terminée")
        
        return data


# Add this class to your serializer.py file
class RapportInterventionSerializer(serializers.Serializer):
    """
    Serializer for generating intervention reports
    """
    intervention_id = serializers.PrimaryKeyRelatedField(
        queryset=Intervention.objects.all(),
        help_text="ID of the intervention to generate a report for"
    )