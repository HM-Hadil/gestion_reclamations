from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import Reclamation
from .serializers import ReclamationSerializer

class ReclamationListCreateView(generics.ListCreateAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Assigner automatiquement l'utilisateur connecté


class ReclamationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReclamationListView(generics.ListAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReclamationByUserView(generics.ListAPIView):
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]  # Seuls les utilisateurs connectés peuvent accéder

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Récupère l'ID de l'utilisateur depuis l'URL
        return Reclamation.objects.filter(user__id=user_id)  # Filtrer les réclamations par utilisateur