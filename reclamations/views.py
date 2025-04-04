from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from .models import (
    Reclamation, 
    ReclamationPC, 
    ReclamationElectrique, 
    ReclamationDivers
)
from .serializers import (
    ReclamationSerializer, 
    ReclamationPCSerializer, 
    ReclamationElectriqueSerializer, 
    ReclamationDiversSerializer
)

class ReclamationCreateView(generics.CreateAPIView):
    """
    Vue pour créer une nouvelle réclamation avec ses détails spécifiques
    """
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        # Ajouter l'utilisateur connecté aux données
        data = request.data.copy()
        data['user'] = request.user.id

        # Définir le statut par défaut
        data['statut'] = data.get('statut', 'en_attente')

        # Gérer les données spécifiques selon la catégorie
        category = data.get('category')
        
        if category == 'pc':
            pc_details = data.get('pc_details', {})
            # Gérer les détails spécifiques du PC
            if pc_details.get('type_probleme') == 'materiel':
                # Vérifier si c'est un matériel standard ou autre
                if pc_details.get('materiel') == 'autre':
                    pc_details['autre_materiel'] = pc_details.get('autre_materiel')
            elif pc_details.get('type_probleme') == 'logiciel':
                # Vérifier si c'est un logiciel standard ou autre
                if pc_details.get('logiciel') == 'autre':
                    pc_details['autre_logiciel'] = pc_details.get('autre_logiciel')
        
        elif category == 'electrique':
            electrique_details = data.get('electrique_details', {})
            # Gérer les détails électriques
            if electrique_details.get('type_probleme') == 'climatiseur':
                # Vérifier si c'est un état standard ou autre
                if electrique_details.get('etat_climatiseur') == 'autre':
                    electrique_details['autre_etat_climatiseur'] = electrique_details.get('autre_etat_climatiseur')
        
        elif category == 'divers':
            divers_details = data.get('divers_details', {})
            # Gérer les détails divers
            if divers_details.get('type_probleme') == 'autre':
                # Vérifier si c'est un état standard ou autre
                if divers_details.get('etat_equipement') == 'autre':
                    divers_details['autre_etat_equipement'] = divers_details.get('autre_etat_equipement')

        # Utiliser le sérialiseur pour créer la réclamation
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReclamationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vue pour récupérer, mettre à jour ou supprimer une réclamation
    """
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class ReclamationListView(generics.ListAPIView):
    """
    Vue pour lister toutes les réclamations de l'utilisateur connecté
    """
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Retourne uniquement les réclamations de l'utilisateur connecté
        return Reclamation.objects.filter(user=self.request.user)

class ReclamationFilterView(generics.ListAPIView):
    """
    Vue pour filtrer les réclamations selon différents critères
    """
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        queryset = Reclamation.objects.filter(user=self.request.user)
        
        # Filtres possibles
        lieu = self.request.query_params.get('lieu', None)
        category = self.request.query_params.get('category', None)
        statut = self.request.query_params.get('statut', None)
        
        if lieu:
            queryset = queryset.filter(lieu=lieu)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset

class ReclamationStatisticsView(generics.GenericAPIView):
    """
    Vue pour obtenir des statistiques sur les réclamations
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Statistiques générales
        total_reclamations = Reclamation.objects.filter(user=request.user).count()
        
        # Statistiques par catégorie
        category_stats = {}
        for category, _ in Reclamation.CATEGORY_CHOICES:
            category_stats[category] = Reclamation.objects.filter(
                user=request.user, 
                category=category
            ).count()
        
        # Statistiques par statut
        statut_stats = {}
        for statut, _ in Reclamation.STATUT_CHOICES:
            statut_stats[statut] = Reclamation.objects.filter(
                user=request.user, 
                statut=statut
            ).count()
        
        return Response({
            'total_reclamations': total_reclamations,
            'category_stats': category_stats,
            'statut_stats': statut_stats
        })

# Viewsets pour chaque type de réclamation détaillée
class ReclamationPCViewSet(viewsets.ModelViewSet):
    queryset = ReclamationPC.objects.all()
    serializer_class = ReclamationPCSerializer
    permission_classes = [IsAuthenticated]

class ReclamationElectriqueViewSet(viewsets.ModelViewSet):
    queryset = ReclamationElectrique.objects.all()
    serializer_class = ReclamationElectriqueSerializer
    permission_classes = [IsAuthenticated]

class ReclamationDiversViewSet(viewsets.ModelViewSet):
    queryset = ReclamationDivers.objects.all()
    serializer_class = ReclamationDiversSerializer
    permission_classes = [IsAuthenticated]
class UserReclamationsView(generics.ListAPIView):
    """
    Liste toutes les réclamations d'un utilisateur spécifique
    avec possibilité de filtrer par statut
    """
    serializer_class = ReclamationSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        status_filter = self.request.query_params.get('status', None)
        
        queryset = Reclamation.objects.filter(user_id=user_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by('-date_creation')


class ReclamationsEnAttenteView(generics.ListAPIView):
    """
    Liste toutes les réclamations avec statut 'en_attente'
    """
    serializer_class = ReclamationSerializer
    queryset = Reclamation.objects.filter(status='en_attente').order_by('-date_creation')

class ReclamationsEnCoursView(generics.ListAPIView):
    """
    Liste toutes les réclamations avec statut 'en_cours'
    """
    serializer_class = ReclamationSerializer
    queryset = Reclamation.objects.filter(status='en_cours').order_by('-date_creation')

class ReclamationsTermineesView(generics.ListAPIView):
    """
    Liste toutes les réclamations avec statut 'termine'
    """
    serializer_class = ReclamationSerializer
    queryset = Reclamation.objects.filter(status='termine').order_by('-date_creation')

class DeleteReclamationView(APIView):
    """
    Supprime une réclamation par son ID
    """
    def delete(self, request, reclamation_id):
        reclamation = get_object_or_404(Reclamation, id=reclamation_id)
        
        # Vérifiez si l'utilisateur est autorisé à supprimer cette réclamation
        # Exemple: administrateur ou propriétaire de la réclamation
        if request.user.is_staff or reclamation.user == request.user:
            reclamation.delete()
            return Response({"message": "Réclamation supprimée avec succès"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Vous n'êtes pas autorisé à supprimer cette réclamation"}, 
                            status=status.HTTP_403_FORBIDDEN)

class UserReclamationsByStatusView(generics.ListAPIView):
    """
    Liste les réclamations d'un utilisateur spécifique filtrées par statut
    """
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        status_value = self.kwargs.get('status')
        
        # Vérifier si le statut est valide
        if status_value not in [choice[0] for choice in Reclamation.STATUS_CHOICES]:
            return Reclamation.objects.none()
            
        return Reclamation.objects.filter(
            user_id=user_id,
            status=status_value
        ).order_by('-date_creation')
    

