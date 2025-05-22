from Intervention.models import Intervention
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.db.models.functions import TruncMonth, ExtractMonth
from django.utils import timezone
from datetime import timedelta

from .models import (
    PC,  # Remplace Equipement
    Reclamation, 
    ReclamationPC, 
    ReclamationElectrique, 
    ReclamationDivers,
    Laboratoire,
)
from .serializers import (
    PCSerializer,  # Remplace EquipementSerializer
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
        data['status'] = data.get('status', 'en_attente')

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
        status = self.request.query_params.get('status', None)
        
        if lieu:
            queryset = queryset.filter(lieu=lieu)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if status:
            queryset = queryset.filter(status=status)
        
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
        status_stats = {}
        for status_value, _ in Reclamation.STATUS_CHOICES:
            status_stats[status_value] = Reclamation.objects.filter(
                user=request.user, 
                status=status_value
            ).count()
        
        return Response({
            'total_reclamations': total_reclamations,
            'category_stats': category_stats,
            'status_stats': status_stats
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

class AnalyseStatistiqueView(APIView):
    """
    Vue pour l'analyse statistique des réclamations et interventions
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        # Période d'analyse (par défaut les 12 derniers mois)
        mois = int(request.query_params.get('mois', 12))
        date_debut = timezone.now() - timedelta(days=30 * mois)
        
        # Filtres optionnels
        laboratoire_id = request.query_params.get('laboratoire_id')
        category = request.query_params.get('category')
        
        # Base des requêtes
        reclamations = Reclamation.objects.filter(date_creation__gte=date_debut)
        interventions = Intervention.objects.filter(date_debut__gte=date_debut)
        
        # Appliquer les filtres si spécifiés
        if laboratoire_id:
            reclamations = reclamations.filter(laboratoire_id=laboratoire_id)
            interventions = interventions.filter(reclamation__laboratoire_id=laboratoire_id)
        
        if category:
            reclamations = reclamations.filter(category=category)
            interventions = interventions.filter(reclamation__category=category)
            
        # 1. Nombre de pannes par mois pour détecter les PCs les plus défaillants
        pannes_par_mois = (
            reclamations
            .annotate(mois=TruncMonth('date_creation'))
            .values('mois')
            .annotate(total=Count('id'))
            .order_by('mois')
        )
        
        # PCs les plus défaillants (remplace equipements_defaillants)
        pcs_defaillants = (
            reclamations
            .filter(pc__isnull=False)
            .values('pc__poste', 'pc__sn_inventaire', 'pc__laboratoire__nom')
            .annotate(total_pannes=Count('id'))
            .order_by('-total_pannes')[:10]
        )
        
        # 2. Taux d'interventions réussies pour évaluer efficacité des techniciens
        interventions_terminees = interventions.filter(date_fin__isnull=False)
        
        taux_interventions_par_technicien = []
        for tech in interventions.values('technicien').annotate(total=Count('id')).order_by('technicien'):
            tech_id = tech['technicien']
            total_interventions = tech['total']
            interventions_reussies = interventions_terminees.filter(
                technicien_id=tech_id,
                reclamation__status='termine'
            ).count()
            
            # Calculer le taux de réussite
            taux_reussite = 0
            if total_interventions > 0:
                taux_reussite = (interventions_reussies / total_interventions) * 100
                
            # Obtenir le nom du technicien
            tech_info = interventions.filter(technicien_id=tech_id).first()
            tech_nom = f"{tech_info.technicien.first_name} {tech_info.technicien.last_name}" if tech_info else f"Technicien {tech_id}"
            
            taux_interventions_par_technicien.append({
                'technicien_id': tech_id,
                'technicien_nom': tech_nom,
                'total_interventions': total_interventions,
                'interventions_reussies': interventions_reussies,
                'taux_reussite': round(taux_reussite, 2)
            })
        
        # 3. Temps moyen de résolution des pannes
        duree_moyenne_resolution = interventions_terminees.annotate(
            duree=ExpressionWrapper(
                F('date_fin') - F('date_debut'),
                output_field=DurationField()
            )
        ).aggregate(temps_moyen=Avg('duree'))
        
        # Convertir la durée en heures
        temps_moyen_heures = None
        if duree_moyenne_resolution['temps_moyen']:
            temps_moyen_secondes = duree_moyenne_resolution['temps_moyen'].total_seconds()
            temps_moyen_heures = round(temps_moyen_secondes / 3600, 2)
        
        # 4. Comparaison entre laboratoires
        statistiques_par_labo = []
        for labo in Laboratoire.objects.all():
            reclamations_labo = reclamations.filter(laboratoire=labo)
            interventions_labo = interventions.filter(reclamation__laboratoire=labo)
            interventions_terminees_labo = interventions_labo.filter(date_fin__isnull=False)
            
            nb_reclamations = reclamations_labo.count()
            nb_reclamations_en_attente = reclamations_labo.filter(status='en_attente').count()
            nb_reclamations_en_cours = reclamations_labo.filter(status='en_cours').count()
            nb_reclamations_terminees = reclamations_labo.filter(status='termine').count()
            
            # Temps moyen de résolution pour ce laboratoire
            duree_moyenne_labo = interventions_terminees_labo.annotate(
                duree=ExpressionWrapper(
                    F('date_fin') - F('date_debut'),
                    output_field=DurationField()
                )
            ).aggregate(temps_moyen=Avg('duree'))
            
            temps_moyen_heures_labo = None
            if duree_moyenne_labo['temps_moyen']:
                temps_moyen_secondes_labo = duree_moyenne_labo['temps_moyen'].total_seconds()
                temps_moyen_heures_labo = round(temps_moyen_secondes_labo / 3600, 2)
            
            statistiques_par_labo.append({
                'laboratoire_id': labo.id,
                'laboratoire_nom': labo.nom,
                'total_reclamations': nb_reclamations,
                'reclamations_en_attente': nb_reclamations_en_attente,
                'reclamations_en_cours': nb_reclamations_en_cours,
                'reclamations_terminees': nb_reclamations_terminees,
                'temps_moyen_resolution': temps_moyen_heures_labo,
                'taux_resolution': round((nb_reclamations_terminees / nb_reclamations) * 100, 2) if nb_reclamations > 0 else 0
            })
        
        # Statistiques par catégorie de problème
        statistiques_par_categorie = []
        for categorie, _ in Reclamation.CATEGORY_CHOICES:
            reclamations_cat = reclamations.filter(category=categorie)
            nb_reclamations_cat = reclamations_cat.count()
            nb_reclamations_terminees_cat = reclamations_cat.filter(status='termine').count()
            
            statistiques_par_categorie.append({
                'categorie': categorie,
                'total_reclamations': nb_reclamations_cat,
                'reclamations_terminees': nb_reclamations_terminees_cat,
                'taux_resolution': round((nb_reclamations_terminees_cat / nb_reclamations_cat) * 100, 2) if nb_reclamations_cat > 0 else 0
            })
            
        # Construire la réponse
        response_data = {
            'pannes_par_mois': list(pannes_par_mois),
            'pcs_defaillants': list(pcs_defaillants),  # Remplace equipements_defaillants
            'taux_interventions_par_technicien': taux_interventions_par_technicien,
            'temps_moyen_resolution': temps_moyen_heures,
            'statistiques_par_laboratoire': statistiques_par_labo,
            'statistiques_par_categorie': statistiques_par_categorie
        }
        
        return Response(response_data)

class PCsByLaboratoireView(generics.ListAPIView):
    """Vue pour récupérer les PCs d'un laboratoire avec informations détaillées"""
    serializer_class = PCSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        laboratoire_id = self.kwargs.get('laboratoire_id')
        return PC.objects.filter(laboratoire_id=laboratoire_id).select_related('laboratoire')
    
    def list(self, request, *args, **kwargs):
        laboratoire_id = self.kwargs.get('laboratoire_id')
        
        # Vérifier que le laboratoire existe
        try:
            laboratoire = Laboratoire.objects.get(id=laboratoire_id)
        except Laboratoire.DoesNotExist:
            return Response({
                'error': f'Le laboratoire avec l\'ID {laboratoire_id} n\'existe pas'
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'laboratoire': {
                'id': laboratoire.id,
                'nom': laboratoire.nom
            },
            'pcs': serializer.data,
            'total_pcs': queryset.count()
        })

class AllReclamationsFilterView(generics.ListAPIView):
    """
    Vue pour filtrer TOUTES les réclamations (sans restriction par utilisateur)
    selon différents critères.
    """
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Start with all Reclamation objects
        queryset = Reclamation.objects.all()

        # Possible filters
        lieu = self.request.query_params.get('lieu', None)
        category = self.request.query_params.get('category', None)
        status_filter = self.request.query_params.get('status', None)
        
        if lieu:
            queryset = queryset.filter(lieu=lieu)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-date_creation')

class CreatePCView(generics.CreateAPIView):
    """Vue pour créer un nouveau PC"""
    serializer_class = PCSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def create(self, request, *args, **kwargs):
        # Vérifier que le laboratoire existe
        laboratoire_id = request.data.get('laboratoire')
        if laboratoire_id:
            try:
                Laboratoire.objects.get(id=laboratoire_id)
            except Laboratoire.DoesNotExist:
                return Response({
                    'error': f'Le laboratoire avec l\'ID {laboratoire_id} n\'existe pas'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)

class PCDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, modifier ou supprimer un PC"""
    queryset = PC.objects.all()
    serializer_class = PCSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class PCListView(generics.ListAPIView):
    """Vue pour lister tous les PCs"""
    queryset = PC.objects.all().select_related('laboratoire')
    serializer_class = PCSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class ReclamationsByPCView(generics.ListAPIView):
    """Vue pour récupérer toutes les réclamations liées à un PC spécifique"""
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        pc_id = self.kwargs.get('pc_id')
        return Reclamation.objects.filter(pc_id=pc_id).order_by('-date_creation')
    
    def list(self, request, *args, **kwargs):
        pc_id = self.kwargs.get('pc_id')
        
        # Vérifier que le PC existe
        try:
            pc = PC.objects.get(id=pc_id)
        except PC.DoesNotExist:
            return Response({
                'error': f'Le PC avec l\'ID {pc_id} n\'existe pas'
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'pc': {
                'id': pc.id,
                'poste': pc.poste,
                'sn_inventaire': pc.sn_inventaire,
                'laboratoire': pc.laboratoire.nom if pc.laboratoire else None
            },
            'reclamations': serializer.data,
            'total_reclamations': queryset.count()
        })

class StatistiquesPCView(APIView):
    """Vue pour obtenir des statistiques sur les PCs"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        # Statistiques générales sur les PCs
        total_pcs = PC.objects.count()
        pcs_avec_laboratoire = PC.objects.filter(laboratoire__isnull=False).count()
        pcs_sans_laboratoire = PC.objects.filter(laboratoire__isnull=True).count()
        
        # PCs par laboratoire
        pcs_par_laboratoire = []
        for labo in Laboratoire.objects.all():
            nb_pcs = PC.objects.filter(laboratoire=labo).count()
            nb_reclamations = Reclamation.objects.filter(
                pc__laboratoire=labo,
                category='pc'
            ).count()
            
            pcs_par_laboratoire.append({
                'laboratoire_id': labo.id,
                'laboratoire_nom': labo.nom,
                'nombre_pcs': nb_pcs,
                'nombre_reclamations_pc': nb_reclamations,
                'taux_reclamations': round((nb_reclamations / nb_pcs) * 100, 2) if nb_pcs > 0 else 0
            })
        
        # PCs les plus problématiques
        pcs_problematiques = (
            PC.objects
            .annotate(nb_reclamations=Count('reclamations'))
            .filter(nb_reclamations__gt=0)
            .order_by('-nb_reclamations')[:10]
        )
        
        pcs_problematiques_data = []
        for pc in pcs_problematiques:
            pcs_problematiques_data.append({
                'pc_id': pc.id,
                'poste': pc.poste,
                'sn_inventaire': pc.sn_inventaire,
                'laboratoire': pc.laboratoire.nom if pc.laboratoire else None,
                'nombre_reclamations': pc.nb_reclamations
            })
        
        return Response({
            'total_pcs': total_pcs,
            'pcs_avec_laboratoire': pcs_avec_laboratoire,
            'pcs_sans_laboratoire': pcs_sans_laboratoire,
            'pcs_par_laboratoire': pcs_par_laboratoire,
            'pcs_problematiques': pcs_problematiques_data
        })

class LaboratoireListView(generics.ListAPIView):
    """Vue pour lister tous les laboratoires avec le nombre de PCs"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        laboratoires_data = []
        
        for labo in Laboratoire.objects.all():
            nb_pcs = PC.objects.filter(laboratoire=labo).count()
            nb_reclamations = Reclamation.objects.filter(laboratoire=labo).count()
            
            laboratoires_data.append({
                'id': labo.id,
                'nom': labo.nom,
                'modele_postes': labo.modele_postes,
                'processeur': labo.processeur,
                'memoire_ram': labo.memoire_ram,
                'stockage': labo.stockage,
                'nombre_pcs': nb_pcs,
                'nombre_reclamations': nb_reclamations
            })
        
        return Response({
            'laboratoires': laboratoires_data,
            'total_laboratoires': len(laboratoires_data)
        })