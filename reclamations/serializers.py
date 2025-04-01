from rest_framework import serializers
from .models import (
    Reclamation, 
    ReclamationPC, 
    ReclamationElectrique, 
    ReclamationDivers
)

class ReclamationPCSerializer(serializers.ModelSerializer):
    """
    Serializer for ReclamationPC model
    """
    autre_materiel = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    autre_logiciel = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ReclamationPC
        fields = '__all__'
        extra_kwargs = {
            'details_probleme': {'required': False},
            'materiel': {'required': False},
            'logiciel': {'required': False},
            'reclamation': {'required': False} 
        }

class ReclamationElectriqueSerializer(serializers.ModelSerializer):
    """
    Serializer for ReclamationElectrique model
    """
    autre_etat_climatiseur = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ReclamationElectrique
        fields = '__all__'
        extra_kwargs = {
            'description_probleme': {'required': False},
            'etat_climatiseur': {'required': False},
            'reclamation': {'required': False}  # Add this line
        }
class ReclamationDiversSerializer(serializers.ModelSerializer):
    """
    Serializer for ReclamationDivers model
    """
    autre_etat_equipement = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ReclamationDivers
        fields = '__all__'
        extra_kwargs = {
            'description_probleme': {'required': False},
            'etat_equipement': {'required': False},
            'reclamation': {'required': False} 
        }

class ReclamationSerializer(serializers.ModelSerializer):
    """
    Main Reclamation serializer with nested detail serializers
    """
    pc_details = ReclamationPCSerializer(required=False, allow_null=True)
    electrique_details = ReclamationElectriqueSerializer(required=False, allow_null=True)
    divers_details = ReclamationDiversSerializer(required=False, allow_null=True)

    class Meta:
        model = Reclamation
        fields = '__all__'
        extra_kwargs = {
            'description_generale': {'required': False},
            'lieu_specifique': {'required': True}
        }

    def create(self, validated_data):
        """
        Custom create method to handle nested serializers
        """
        # Extract nested serializer data
        pc_details = validated_data.pop('pc_details', None)
        electrique_details = validated_data.pop('electrique_details', None)
        divers_details = validated_data.pop('divers_details', None)

        # Create the main Reclamation instance
        reclamation = Reclamation.objects.create(**validated_data)

        # Create associated details based on category
        try:
            if reclamation.category == 'pc' and pc_details:
                pc_details['reclamation'] = reclamation
                ReclamationPC.objects.create(**pc_details)
            elif reclamation.category == 'electrique' and electrique_details:
                electrique_details['reclamation'] = reclamation
                ReclamationElectrique.objects.create(**electrique_details)
            elif reclamation.category == 'divers' and divers_details:
                divers_details['reclamation'] = reclamation
                ReclamationDivers.objects.create(**divers_details)
        except Exception as e:
            # If creating associated details fails, delete the main reclamation
            reclamation.delete()
            raise serializers.ValidationError(f"Error creating associated details: {str(e)}")

        return reclamation

    def validate(self, data):
        """
        Additional validation to ensure correct details are provided based on category
        """
        category = data.get('category')
        
        # Validate PC details
        if category == 'pc':
            pc_details = data.get('pc_details')
            if not pc_details:
                raise serializers.ValidationError("PC details are required for PC category")
            
            type_probleme = pc_details.get('type_probleme')
            if type_probleme == 'materiel':
                materiel = pc_details.get('materiel')
                if materiel == 'autre' and not pc_details.get('autre_materiel'):
                    raise serializers.ValidationError("'autre_materiel' is required when materiel is 'autre'")
            
            if type_probleme == 'logiciel':
                logiciel = pc_details.get('logiciel')
                if logiciel == 'autre' and not pc_details.get('autre_logiciel'):
                    raise serializers.ValidationError("'autre_logiciel' is required when logiciel is 'autre'")
        
        # Validate Electrique details
        elif category == 'electrique':
            electrique_details = data.get('electrique_details')
            if not electrique_details:
                raise serializers.ValidationError("Electrique details are required for Electrique category")
            
            if electrique_details.get('type_probleme') == 'climatiseur':
                etat_climatiseur = electrique_details.get('etat_climatiseur')
                if etat_climatiseur == 'autre' and not electrique_details.get('autre_etat_climatiseur'):
                    raise serializers.ValidationError("'autre_etat_climatiseur' is required when etat_climatiseur is 'autre'")
        
        # Validate Divers details
        elif category == 'divers':
            divers_details = data.get('divers_details')
            if not divers_details:
                raise serializers.ValidationError("Divers details are required for Divers category")
            
            etat_equipement = divers_details.get('etat_equipement')
            if etat_equipement == 'autre' and not divers_details.get('autre_etat_equipement'):
                raise serializers.ValidationError("'autre_etat_equipement' is required when etat_equipement is 'autre'")
        
        return data