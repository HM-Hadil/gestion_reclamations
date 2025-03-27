from rest_framework import generics, permissions
from .models import Reclamation, ReclamationPC, ReclamationElectrique, ReclamationDivers
from .serializers import (
    ReclamationSerializer, 
    ReclamationPCSerializer, 
    ReclamationElectriqueSerializer, 
    ReclamationDiversSerializer
)
from rest_framework.generics import ListAPIView


class ReclamationListCreateView(ListAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReclamationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReclamationPCListCreateView(generics.ListCreateAPIView):
    queryset = ReclamationPC.objects.all()
    serializer_class = ReclamationPCSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReclamationElectriqueListCreateView(generics.ListCreateAPIView):
    queryset = ReclamationElectrique.objects.all()
    serializer_class = ReclamationElectriqueSerializer
    permission_classes = [permissions.IsAuthenticated]
class ReclamationByUserView(generics.ListAPIView):
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Récupérer l'ID de l'utilisateur depuis l'URL
        return Reclamation.objects.filter(user__id=user_id)  # Filtrer les réclamations par utilisateur


class ReclamationDiversListCreateView(generics.ListCreateAPIView):
    queryset = ReclamationDivers.objects.all()
    serializer_class = ReclamationDiversSerializer
    permission_classes = [permissions.IsAuthenticated]
