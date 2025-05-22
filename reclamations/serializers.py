from rest_framework import serializers
from .models import (
    Reclamation, 
    ReclamationPC, 
    ReclamationElectrique, 
    ReclamationDivers,
    PC,
    Laboratoire
)

class PCSerializer(serializers.ModelSerializer):
    """Serializer pour les PCs"""
    laboratoire_nom = serializers.CharField(source='laboratoire.nom', read_only=True)
    
    class Meta:
        model = PC
        fields = ['id', 'poste', 'sn_inventaire', 'logiciels_installes', 'ecran', 'laboratoire', 'laboratoire_nom']

class ReclamationPCSerializer(serializers.ModelSerializer):
    """Serializer for ReclamationPC model"""
    autre_materiel = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    autre_logiciel = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ReclamationPC
        fields = '__all__'
        extra_kwargs = {
            'description_probleme': {'required': False},
            'reclamation': {'required': False} 
        }

class ReclamationElectriqueSerializer(serializers.ModelSerializer):
    """Serializer for ReclamationElectrique model"""
    autre_etat_climatiseur = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ReclamationElectrique
        fields = '__all__'
        extra_kwargs = {
            'description_probleme': {'required': False},
            'reclamation': {'required': False}
        }

class ReclamationDiversSerializer(serializers.ModelSerializer):
    """Serializer for ReclamationDivers model"""
    autre_etat_equipement = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = ReclamationDivers
        fields = '__all__'
        extra_kwargs = {
            'description_probleme': {'required': False},
            'reclamation': {'required': False} 
        }

class ReclamationSerializer(serializers.ModelSerializer):
    """Main Reclamation serializer with nested detail serializers"""
    pc_details = ReclamationPCSerializer(required=False, allow_null=True)
    electrique_details = ReclamationElectriqueSerializer(required=False, allow_null=True)
    divers_details = ReclamationDiversSerializer(required=False, allow_null=True)
    pcs_disponibles = serializers.SerializerMethodField()
    pc_info = PCSerializer(source='pc', read_only=True)
    laboratoire_nom = serializers.CharField(source='laboratoire.nom', read_only=True)

    class Meta:
        model = Reclamation
        fields = '__all__'
        extra_kwargs = {
            'description_generale': {'required': False},
            'status': {'required': False} 
        }
    
    def get_pcs_disponibles(self, obj):
        """Retourne les PCs disponibles pour le laboratoire sélectionné"""
        if obj.laboratoire:
            pcs = PC.objects.filter(laboratoire=obj.laboratoire)
            return PCSerializer(pcs, many=True).data
        return []

    def create(self, validated_data):
        """Custom create method to handle nested serializers and PC assignment"""
        # Extract nested serializer data
        pc_details = validated_data.pop('pc_details', None)
        electrique_details = validated_data.pop('electrique_details', None)
        divers_details = validated_data.pop('divers_details', None)

        # Create the main Reclamation instance
        reclamation = Reclamation.objects.create(**validated_data)

        # Assigner automatiquement le PC si c'est une réclamation PC et aucun PC n'est spécifié
        if reclamation.category == 'pc' and not reclamation.pc and reclamation.laboratoire:
            self.assigner_pc_automatique(reclamation)

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
    
    def assigner_pc_automatique(self, reclamation):
        """Assigne automatiquement un PC du laboratoire (optionnel)"""
        if not reclamation.pc and reclamation.laboratoire:
            # Prendre le premier PC disponible du laboratoire
            pc = PC.objects.filter(laboratoire=reclamation.laboratoire).first()
            if pc:
                reclamation.pc = pc
                reclamation.save()

    def validate(self, data):
        """Additional validation to ensure correct details are provided based on category"""
        category = data.get('category')
        
        # Validation spécifique pour les réclamations PC
        if category == 'pc':
            pc_details = data.get('pc_details')
            if not pc_details:
                raise serializers.ValidationError("PC details are required for PC category")
            
            # Vérifier qu'un PC est spécifié ou qu'un laboratoire est fourni
            if not data.get('pc') and not data.get('laboratoire'):
                raise serializers.ValidationError("Either a specific PC or a laboratory must be specified for PC complaints")
        
        # Validate Electrique details
        elif category == 'electrique':
            electrique_details = data.get('electrique_details')
            if not electrique_details:
                raise serializers.ValidationError("Electrique details are required for Electrique category")
        
        # Validate Divers details
        elif category == 'divers':
            divers_details = data.get('divers_details')
            if not divers_details:
                raise serializers.ValidationError("Divers details are required for Divers category")
        
        return data