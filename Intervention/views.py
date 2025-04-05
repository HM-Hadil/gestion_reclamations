from django.shortcuts import render, get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from rest_framework_simplejwt.authentication import JWTAuthentication
import io
from .models import Intervention
from reclamations.models import Reclamation
from reclamations.serializers import ReclamationSerializer
from .serializer import InterventionSerializer, RapportInterventionSerializer


from .serializer import InterventionSerializer

from .serializer import InterventionSerializer, RapportInterventionSerializer

class InterventionViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les interventions
    """
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Associer le technicien actuel à l'intervention
        serializer.save(technicien=self.request.user)

class UserInterventionsView(generics.ListAPIView):
    """
    Liste les interventions effectuées par un technicien spécifique
    """
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Intervention.objects.filter(technicien_id=user_id)

class FinirInterventionView(APIView):
    """
    Marquer une intervention comme terminée
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, intervention_id):
        intervention = get_object_or_404(Intervention, id=intervention_id)
        
        # Vérifier que l'utilisateur est le technicien assigné
        if intervention.technicien != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à modifier cette intervention"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Mettre à jour l'intervention
        intervention.status = 'terminee'
        intervention.date_fin = timezone.now()
        intervention.save()  # Le signal dans save() mettra à jour la réclamation
        
        return Response(
            {"message": "Intervention marquée comme terminée avec succès"},
            status=status.HTTP_200_OK
        )

class GenererRapportView(APIView):
    """
    Générer un rapport PDF à partir d'une intervention
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = RapportInterventionSerializer(data=request.data)
        
        if serializer.is_valid():
            intervention = serializer.validated_data['intervention_id']
            
            # Préparer les données du contexte pour le template
            context = {
                'intervention': intervention,
                'date_rapport': timezone.now().strftime('%d/%m/%Y'),
                'technicien_nom': f"{intervention.technicien.first_name} {intervention.technicien.last_name}",
                'reclamation': intervention.reclamation,
                'date_debut': intervention.date_debut.strftime('%d/%m/%Y'),
                'date_fin': intervention.date_fin.strftime('%d/%m/%Y') if intervention.date_fin else 'En cours'
            }
            
            # Générer le HTML à partir du template
            html_string = render_to_string('rapports/intervention_rapport.html', context)
            
            # Convertir le HTML en PDF en utilisant BytesIO
            pdf_file = io.BytesIO()
            HTML(string=html_string).write_pdf(pdf_file)
            pdf_file.seek(0)
            
            # Créer une réponse HTTP avec le contenu PDF
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="rapport_intervention_{intervention.id}.pdf"'
            return response
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class FinirInterventionView(APIView):
    """
    Marquer une intervention comme terminée et mettre à jour le statut de la réclamation
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, intervention_id):
        intervention = get_object_or_404(Intervention, id=intervention_id)
        
        # Vérifier que l'utilisateur est le technicien assigné
        if intervention.technicien != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à modifier cette intervention"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mettre à jour les données de l'intervention
        intervention.probleme_constate = request.data.get('probleme_constate', intervention.probleme_constate)
        intervention.analyse_cause = request.data.get('analyse_cause', intervention.analyse_cause)
        intervention.actions_entreprises = request.data.get('actions_entreprises', intervention.actions_entreprises)
        intervention.pieces_remplacees = request.data.get('pieces_remplacees', intervention.pieces_remplacees)
        intervention.resultat_tests = request.data.get('resultat_tests', intervention.resultat_tests)
        intervention.recommandations = request.data.get('recommandations', intervention.recommandations)
        intervention.mots_cles = request.data.get('mots_cles', intervention.mots_cles)
        
        # Terminer l'intervention (cette méthode met également à jour le statut de la réclamation)
        intervention.terminer()
        
        return Response(
            {
                "message": "Intervention marquée comme terminée avec succès",
                "intervention": InterventionSerializer(intervention).data
            },
            status=status.HTTP_200_OK
        )
    
class CreateInterventionView(APIView):
    """
    Vue pour créer une intervention liée à une réclamation
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, reclamation_id):
        reclamation = get_object_or_404(Reclamation, id=reclamation_id)
        
        # Préparer les données pour l'intervention
        data = request.data.copy()
        data['reclamation'] = reclamation_id
        data['technicien'] = request.user.id
        
        # Créer l'intervention
        serializer = InterventionSerializer(data=data)
        
        if serializer.is_valid():
            intervention = serializer.save()
            
            # Mettre à jour le statut de la réclamation à "en_cours"
            reclamation.status = 'en_cours'
            reclamation.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateReclamationStatusView(APIView):
    """
    Vue pour mettre à jour le statut d'une réclamation
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def put(self, request, reclamation_id):
        reclamation = get_object_or_404(Reclamation, id=reclamation_id)
        
        # Vérifier que l'utilisateur est autorisé (propriétaire de la réclamation ou admin)
        if reclamation.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "Vous n'êtes pas autorisé à modifier cette réclamation"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer le nouveau statut
        new_status = request.data.get('status')
        
        # Vérifier que le statut est valide
        if new_status not in [choice[0] for choice in Reclamation.STATUS_CHOICES]:
            return Response(
                {"error": f"Statut invalide. Les statuts valides sont: {[choice[0] for choice in Reclamation.STATUS_CHOICES]}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le statut
        reclamation.status = new_status
        reclamation.save()
        
        # Sérialiser et retourner la réclamation mise à jour
        serializer = ReclamationSerializer(reclamation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReclamationDetailView(APIView):
    """
    Vue pour récupérer les détails d'une réclamation spécifique
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, reclamation_id):
        reclamation = get_object_or_404(Reclamation, id=reclamation_id)
        
        # Vérifier que l'utilisateur est autorisé (technicien assigné ou admin)
        if not request.user.is_staff and reclamation.user != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à accéder à cette réclamation"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Sérialiser et retourner la réclamation
        serializer = ReclamationSerializer(reclamation)
        return Response(serializer.data, status=status.HTTP_200_OK)