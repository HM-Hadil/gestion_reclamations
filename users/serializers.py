from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'image', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': True}
        }
        
    def get_image(self, obj):
        if obj.image:
            # Utiliser l'URL complète pour l'image
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(settings.MEDIA_URL + str(obj.image))
            return settings.MEDIA_URL + str(obj.image)
        return None
    
    def create(self, validated_data):
        # Générer un nom d'utilisateur à partir de l'email
        validated_data['username'] = validated_data['email']
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Ce champ est requis.'})
            
        # Créer l'utilisateur avec tous les champs requis
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'user')  # Utilisation de get avec une valeur par défaut
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Explicitement définir comme ImageField
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password', 'image']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # Rendre le mot de passe optionnel
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def get_image(self, obj):
        if obj.image:
            # Utiliser l'URL complète pour l'image
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(settings.MEDIA_URL + str(obj.image))
            return settings.MEDIA_URL + str(obj.image)
        return None
    
    def update(self, instance, validated_data):
        # Gérer la mise à jour du mot de passe uniquement s'il est fourni
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance