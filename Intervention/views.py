from django.shortcuts import render

from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

from .models import Intervention, Reclamation
from .serializers import InterventionSerializer, RapportInterventionSerializer

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
            
            # Convertir le HTML en PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf') as output:
                HTML(string=html_string).write_pdf(output.name)
                output.seek(0)
                response = HttpResponse(output.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="rapport_intervention_{intervention.id}.pdf"'
                return response
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)