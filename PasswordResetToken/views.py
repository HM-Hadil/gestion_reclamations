from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordResetToken

import uuid


User = get_user_model()

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Aucun utilisateur trouvé avec cet email."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Générer un token unique
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=1)
        
        # Créer le token de réinitialisation
        reset_token = PasswordResetToken.objects.create(
            user=user, 
            token=token, 
            expires_at=expires_at
        )
        
        # URL de réinitialisation
        reset_link = f"http://127.0.0.1:8000/reset-password/{token}/"
        
        # Envoyer l'email
        send_mail(
            "Réinitialisation de votre mot de passe",
            f"""Bonjour {user.first_name} {user.last_name},

Vous avez demandé à réinitialiser votre mot de passe.
Cliquez sur le lien suivant pour le réinitialiser :
{reset_link}

Ce lien expirera dans 1 heure.

Si vous n'avez pas demandé cette réinitialisation,
ignorez simplement cet email.

Cordialement,
Votre équipe""",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response(
            {"message": "Un email de réinitialisation a été envoyé."}, 
            status=status.HTTP_200_OK
        )
class ResetPasswordView(APIView):
    def get(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            # Vérifier la validité du token
            if not reset_token.is_valid():
                return Response(
                    {"error": "Le lien de réinitialisation a expiré."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Renvoyez une réponse indiquant que le token est valide
            return Response({
                "message": "Token valide. Vous pouvez réinitialiser votre mot de passe.",
                "user_email": reset_token.user.email
            }, status=status.HTTP_200_OK)
        
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Token de réinitialisation invalide."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Token de réinitialisation invalide."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier l'expiration du token
        if not reset_token.is_valid():
            return Response(
                {"error": "Le lien de réinitialisation a expiré."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer le nouveau mot de passe
        new_password = request.data.get("password")
        if not new_password:
            return Response(
                {"error": "Nouveau mot de passe requis."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le mot de passe de l'utilisateur
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Supprimer le token après utilisation
        reset_token.delete()
        
        return Response(
            {"message": "Mot de passe réinitialisé avec succès."}, 
            status=status.HTTP_200_OK
        )