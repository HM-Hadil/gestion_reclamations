from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

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
        fields = ['first_name', 'last_name', 'password']  # Include fields you want to update

    def update(self, instance, validated_data):
        # Get the password field from validated data, if present
        password = validated_data.get('password', None)
        
        # If the password is provided, hash it before saving
        if password:
            instance.set_password(password)
        
        # Save the other fields
        return super().update(instance, validated_data)