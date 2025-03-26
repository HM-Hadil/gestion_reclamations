from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'image')

    def get_image(self, obj):
        if obj.image:
            return settings.MEDIA_URL + str(obj.image)
        return None

    def create(self, validated_data):
        # Générer un nom d'utilisateur à partir de l'email
        validated_data['username'] = validated_data['email']
        
        # Créer l'utilisateur avec tous les champs requis
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role']
        )
        return user
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password', 'image']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # Rendre le mot de passe optionnel
            'image': {'required': False},  # Rendre l'image optionnelle
        }

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