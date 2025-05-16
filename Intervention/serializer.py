# Assuming this is in your app's serializer.py (e.g., interventions/serializer.py)

from rest_framework import serializers
from .models import Intervention # Assuming Intervention model is in the same app
from reclamations.models import Reclamation # Assuming Reclamation model is in reclamations app
from django.contrib.auth import get_user_model # Import to get the User model

User = get_user_model()

# --- Serializers pour les opérations générales ---

class InterventionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Intervention (pour CRUD général, listage, etc.)
    Inclut tous les champs pour la création initiale avec les données du rapport.
    """
    reclamation_details = serializers.SerializerMethodField()
    technicien_nom = serializers.SerializerMethodField()
    # Mark technicien as read_only=True
    technicien = serializers.PrimaryKeyRelatedField(read_only=True)
    # Add URL fields for fichier_joint and rapport_pdf
    fichier_joint_url = serializers.SerializerMethodField()
    rapport_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Intervention
        fields = '__all__'
        read_only_fields = ['date_debut', 'date_fin', 'rapport_pdf'] # date_debut est auto_now_add, date_fin est défini par .terminer()

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
            try:
                pc_details = reclamation.pc_details # Adaptez si le related_name est différent
                details['details_specifiques'] = {
                    'type_probleme': pc_details.type_probleme,
                    'description_probleme': pc_details.description_probleme
                }
            except Reclamation.pc_details.RelatedObjectDoesNotExist: # Adaptez si le related_name est différent
                pass # Gérer le cas où les détails spécifiques n'existent pas

        elif reclamation.category == 'electrique' and hasattr(reclamation, 'electrique_details'):
            try:
                electrique_details = reclamation.electrique_details # Adaptez si le related_name est différent
                details['details_specifiques'] = {
                    'type_probleme': electrique_details.type_probleme,
                    'description_probleme': electrique_details.description_probleme
                }
            except Reclamation.electrique_details.RelatedObjectDoesNotExist: # Adaptez si le related_name est différent
                pass

        elif reclamation.category == 'divers' and hasattr(reclamation, 'divers_details'):
            try:
                divers_details = reclamation.divers_details # Adaptez si le related_name est différent
                details['details_specifiques'] = {
                    'type_probleme': divers_details.type_probleme,
                    'description_probleme': divers_details.description_probleme
                }
            except Reclamation.divers_details.RelatedObjectDoesNotExist: # Adaptez si le related_name est différent
                pass

        return details

    def get_technicien_nom(self, obj):
        """Retourne le nom complet du technicien"""
        if obj.technicien:
             # Assurez-vous que le modèle User a first_name et last_name
             return f"{obj.technicien.first_name} {obj.technicien.last_name}"
        return "N/A" # Gérer le cas où technicien est null (si possible dans votre modèle)
    
    def get_fichier_joint_url(self, obj):
        """Retourne l'URL du fichier joint s'il existe"""
        if obj.fichier_joint:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.fichier_joint.url)
            return obj.fichier_joint.url
        return None
    
    def get_rapport_pdf_url(self, obj):
        """Retourne l'URL du rapport PDF s'il existe"""
        if obj.rapport_pdf:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.rapport_pdf.url)
            return obj.rapport_pdf.url
        return None

    # Validation personnalisée pour la création d'intervention (si nécessaire)
    def validate(self, data):
        """Validation personnalisée pour la création d'intervention."""
        # Vérifier que la réclamation n'est pas déjà terminée lors de la création
        reclamation = data.get('reclamation')
        if reclamation and reclamation.status == 'termine':
            raise serializers.ValidationError({"reclamation": "Cette réclamation est déjà terminée."})

        return data


# --- Serializer Spécifique pour la réception des données du rapport ---
class InterventionReportDataSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les données du rapport.
    Utilisé principalement pour les mises à jour partielles si nécessaire.
    """
    class Meta:
        model = Intervention
        fields = [
            'probleme_constate',
            'analyse_cause',
            'actions_entreprises',
            'pieces_remplacees',
            'resultat_tests',
            'recommandations',
            'mots_cles',
            'fichier_joint', # Inclure le champ fichier pour l'upload
        ]