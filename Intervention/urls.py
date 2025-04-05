from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Vues existantes
    InterventionViewSet,
    UserInterventionsView,
    FinirInterventionView,
    GenererRapportView,
    # Nouvelles vues
    UpdateReclamationStatusView,
    CreateInterventionView
)

# Router pour les viewsets
router = DefaultRouter()
router.register('interventions', InterventionViewSet)

urlpatterns = [
    # URLs existantes
    path('interventions/user/<int:user_id>/', UserInterventionsView.as_view(), name='user-interventions'),
    path('interventions/<int:intervention_id>/terminer/', FinirInterventionView.as_view(), name='terminer-intervention'),
    path('interventions/rapport/', GenererRapportView.as_view(), name='generer-rapport'),
    
    # Nouvelles URLs
    path('reclamations/<int:reclamation_id>/update-status/', UpdateReclamationStatusView.as_view(), name='update-reclamation-status'),
    path('reclamations/<int:reclamation_id>/create-intervention/', CreateInterventionView.as_view(), name='create-intervention'),
    
    # Inclure les routes du router
    path('', include(router.urls))
]