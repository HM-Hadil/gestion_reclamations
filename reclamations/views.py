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
    Reclamation, 
    ReclamationPC, 
    ReclamationElectrique, 
    ReclamationDivers,
    Laboratoire,
     
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
            
        # 1. Nombre de pannes par mois pour détecter les équipements les plus défaillants
        pannes_par_mois = (
            reclamations
            .annotate(mois=TruncMonth('date_creation'))
            .values('mois')
            .annotate(total=Count('id'))
            .order_by('mois')
        )
        
        # Équipements les plus défaillants
        equipements_defaillants = (
            reclamations
            .filter(equipement__isnull=False)
            .values('equipement__identificateur', 'equipement__type')
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
        
        # Convertir la durée en heures (ou en format plus lisible)
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
            
            # Calculer les statistiques pour ce laboratoire
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
            'equipements_defaillants': list(equipements_defaillants),
            'taux_interventions_par_technicien': taux_interventions_par_technicien,
            'temps_moyen_resolution': temps_moyen_heures,
            'statistiques_par_laboratoire': statistiques_par_labo,
            'statistiques_par_categorie': statistiques_par_categorie
        }
        
        return Response(response_data)
class AllReclamationsFilterView(generics.ListAPIView):
    """
    Vue pour filtrer TOUTES les réclamations (sans restriction par utilisateur)
    selon différents critères.
    """
    serializer_class = ReclamationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] # Keep if authentication is required for all reclamations

    def get_queryset(self):
        # Start with all Reclamation objects
        queryset = Reclamation.objects.all()

        # Possible filters (same as your existing view)
        lieu = self.request.query_params.get('lieu', None)
        category = self.request.query_params.get('category', None)
        statut = self.request.query_params.get('statut', None)
        
        if lieu:
            queryset = queryset.filter(lieu=lieu)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if statut:
            # Ensure 'statut' here matches the field name in your Reclamation model
            queryset = queryset.filter(status=statut) # Assuming the field is 'status' not 'statut' based on typical Django conventions

        return queryset
