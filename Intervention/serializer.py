# interventions/serializers.py
from rest_framework import serializers
from .models import Intervention
from reclamations.models import Reclamation
from django.contrib.auth import get_user_model

User = get_user_model()

# Add a User serializer for technician details
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email'] # Adjust fields as needed

class InterventionSerializer(serializers.ModelSerializer):
    reclamation_details = serializers.SerializerMethodField()
    technicien_nom = serializers.SerializerMethodField()
    technicien = serializers.PrimaryKeyRelatedField(read_only=True)
    fichier_joint_url = serializers.SerializerMethodField()
    rapport_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Intervention
        fields = '__all__'
        read_only_fields = ['date_debut', 'date_fin', 'rapport_pdf']

    def get_reclamation_details(self, obj):
        reclamation = obj.reclamation
        details = {
            'id': reclamation.id,
            'category': reclamation.get_category_display(),
            'lieu': reclamation.get_lieu_display(),
            'laboratoire': reclamation.laboratoire.nom if reclamation.laboratoire else None,
            'description_generale': reclamation.description_generale,
            'date_creation': reclamation.date_creation,
            'status': reclamation.get_status_display()
        }

        # Handle specific details based on category (existing logic)
        if reclamation.category == 'pc' and hasattr(reclamation, 'pc_details'):
            try:
                pc_details = reclamation.pc_details
                details['details_specifiques'] = {
                    'type_probleme': pc_details.type_probleme,
                    'description_probleme': pc_details.description_probleme
                }
            except Reclamation.pc_details.RelatedObjectDoesNotExist:
                pass
        elif reclamation.category == 'electrique' and hasattr(reclamation, 'electrique_details'):
            try:
                electrique_details = reclamation.electrique_details
                details['details_specifiques'] = {
                    'type_probleme': electrique_details.type_probleme,
                    'description_probleme': electrique_details.description_probleme
                }
            except Reclamation.electrique_details.RelatedObjectDoesNotExist:
                pass
        elif reclamation.category == 'divers' and hasattr(reclamation, 'divers_details'):
            try:
                divers_details = reclamation.divers_details
                details['details_specifiques'] = {
                    'type_probleme': divers_details.type_probleme,
                    'description_probleme': divers_details.description_probleme
                }
            except Reclamation.divers_details.RelatedObjectDoesNotExist:
                pass

        return details

    def get_technicien_nom(self, obj):
        if obj.technicien:
            return f"{obj.technicien.first_name} {obj.technicien.last_name}"
        return "N/A"

    def get_fichier_joint_url(self, obj):
        if obj.fichier_joint:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.fichier_joint.url)
            return obj.fichier_joint.url
        return None

    def get_rapport_pdf_url(self, obj):
        if obj.rapport_pdf:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.rapport_pdf.url)
            return obj.rapport_pdf.url
        return None

    def validate(self, data):
        reclamation = data.get('reclamation')
        if reclamation and reclamation.status == 'termine':
            raise serializers.ValidationError({"reclamation": "Cette réclamation est déjà terminée."})
        return data

class InterventionReportDataSerializer(serializers.ModelSerializer):
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
            'fichier_joint',
        ]