import io
from itertools import count
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication

from weasyprint import HTML

from .models import Intervention
from reclamations.models import Reclamation
from .serializer import InterventionSerializer, InterventionReportDataSerializer, UserSerializer
from reclamations.serializers import ReclamationSerializer

User = get_user_model()
def generate_intervention_pdf(intervention: Intervention):
    """
    Génère le PDF du rapport d'intervention et le retourne en tant que ContentFile
    """
    context = {
        'intervention': intervention,
        'date_rapport': timezone.now().strftime('%d/%m/%Y %H:%M'),
        'technicien_nom': f"{intervention.technicien.first_name} {intervention.technicien.last_name}" if intervention.technicien else "N/A",
        'reclamation': intervention.reclamation,
        'date_debut': intervention.date_debut.strftime('%d/%m/%Y %H:%M') if intervention.date_debut else 'N/A',
        'date_fin': intervention.date_fin.strftime('%d/%m/%Y %H:%M') if intervention.date_fin else 'En cours',
        'reclamation_details_specific': None
    }

    reclamation = intervention.reclamation
    details_specific = {}

    if reclamation.category == 'pc' and hasattr(reclamation, 'pc_details'):
        try:
            pc_details = reclamation.pc_details
            details_specific = {
                'type_probleme': pc_details.type_probleme,
                'description_probleme': pc_details.description_probleme
            }
        except Reclamation.pc_details.RelatedObjectDoesNotExist:
            pass

    elif reclamation.category == 'electrique' and hasattr(reclamation, 'electrique_details'):
        try:
            electrique_details = reclamation.electrique_details
            details_specific = {
                'type_probleme': electrique_details.type_probleme,
                'description_probleme': electrique_details.description_probleme
            }
        except Reclamation.electrique_details.RelatedObjectDoesNotExist:
            pass

    elif reclamation.category == 'divers' and hasattr(reclamation, 'divers_details'):
        try:
            divers_details = reclamation.divers_details
            details_specific = {
                'type_probleme': divers_details.type_probleme,
                'description_probleme': divers_details.description_probleme
            }
        except Reclamation.divers_details.RelatedObjectDoesNotExist:
            pass

    context['reclamation_details_specific'] = details_specific

    html_string = render_to_string('rapports/intervention_rapport.html', context)
    pdf_file = io.BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)

    return ContentFile(pdf_file.read(), name=f'rapport_intervention_{intervention.id}.pdf')

def generate_intervention_pdf_response(intervention: Intervention) -> HttpResponse:
    """
    Génère la réponse HTTP contenant le PDF du rapport d'intervention
    """
    if intervention.rapport_pdf:
        intervention.rapport_pdf.open('rb')
        pdf_content = intervention.rapport_pdf.read()
        intervention.rapport_pdf.close()
    else:
        pdf_content_file = generate_intervention_pdf(intervention)
        pdf_content = pdf_content_file.read()

        intervention.rapport_pdf.save(
            f'rapport_intervention_{intervention.id}.pdf',
            pdf_content_file,
            save=True
        )

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_intervention_{intervention.id}.pdf"'
    return response

class CompleteInterventionReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        intervention = get_object_or_404(Intervention, pk=pk)

        if request.user != intervention.technicien and not request.user.is_staff:
            return Response({'detail': 'Vous n\'avez pas la permission de compléter cette intervention.'},
                            status=status.HTTP_403_FORBIDDEN)

        if intervention.reclamation.status == 'termine':
            return Response({'detail': 'La réclamation associée est déjà terminée.'},
                            status=status.HTTP_400_BAD_REQUEST)

        report_data = request.data.get('report_data', {})
        if report_data:
            serializer = InterventionReportDataSerializer(intervention, data=report_data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        intervention.terminer()

        if not intervention.rapport_pdf:
            pdf_content = generate_intervention_pdf(intervention)
            intervention.rapport_pdf.save(
                f'rapport_intervention_{intervention.id}.pdf',
                pdf_content,
                save=True
            )

        pdf_response = generate_intervention_pdf_response(intervention)
        return pdf_response

class InterventionViewSet(viewsets.ModelViewSet):
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        reclamation_id = self.request.query_params.get('reclamation', None)
        if reclamation_id is not None:
            queryset = queryset.filter(reclamation_id=reclamation_id)
        return queryset

    def perform_create(self, serializer):
        intervention = serializer.save(technicien=self.request.user)

        fichier_joint = self.request.FILES.get('fichier_joint')
        if fichier_joint:
            intervention.fichier_joint = fichier_joint
            intervention.save()

class UserInterventionsView(generics.ListAPIView):
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Intervention.objects.filter(technicien_id=user_id)

class CreateInterventionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reclamation_id=None):
        if reclamation_id:
            request.data['reclamation'] = reclamation_id
        else:
            reclamation_id = request.data.get('reclamation')

        if not reclamation_id:
            return Response(
                {"error": "ID de réclamation manquant dans les données de la requête."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(reclamation_id, str):
            try:
                reclamation_id = int(reclamation_id)
            except ValueError:
                return Response(
                    {"error": "ID de réclamation invalide."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        reclamation = get_object_or_404(Reclamation, id=reclamation_id)

        if reclamation.status == 'termine':
            return Response(
                {"error": "Cette réclamation est déjà terminée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['technicien'] = request.user.id

        serializer = InterventionSerializer(data=data)

        if serializer.is_valid():
            intervention = serializer.save(technicien=request.user)

            fichier_joint = request.FILES.get('fichier_joint')
            if fichier_joint:
                intervention.fichier_joint = fichier_joint
                intervention.save()

            reclamation.status = 'en_cours'
            reclamation.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OtherUsersInterventionsView(generics.ListAPIView):
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Intervention.objects.exclude(technicien=self.request.user)

class AllInterventionsView(generics.ListAPIView):
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

class InterventionStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Intervention.objects.all()
        
        # Filter by technician if technician_id is provided in query params
        technician_id = request.query_params.get('technician_id', None)
        if technician_id:
            try:
                technician_id = int(technician_id)
                queryset = queryset.filter(technicien_id=technician_id)
            except ValueError:
                return Response({"error": "Invalid technician_id"}, status=status.HTTP_400_BAD_REQUEST)

        total_interventions = queryset.count()

        # Get technician distribution
        technician_distribution = queryset.values('technicien').annotate(count=count('technicien'))
        technician_stats = {str(item['technicien']): item['count'] for item in technician_distribution}

        # Get status distribution
        status_distribution = queryset.values('reclamation__status').annotate(count=count('reclamation__status'))
        status_stats = {item['reclamation__status']: item['count'] for item in status_distribution}

        # Get data for all technicians (for dropdown)
        all_technicians = User.objects.filter(is_staff=True) # Assuming technicians are staff users
        technicians_data = UserSerializer(all_technicians, many=True).data

        return Response({
            'total_interventions': total_interventions,
            'technician_distribution': technician_stats,
            'status_distribution': status_stats,
            'technicians_data': technicians_data, # Include full technician data
        }, status=status.HTTP_200_OK)