# urls.py - Configuration des URLs améliorée

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompleteInterventionReportView,
    InterventionViewSet,
    UserInterventionsView,
    CreateInterventionView,
)

# Router pour les viewsets
router = DefaultRouter()
router.register('interventions', InterventionViewSet)

urlpatterns = [
    # URL pour obtenir les interventions d'un utilisateur spécifique
    path('interventions/user/<int:user_id>/', UserInterventionsView.as_view(), name='user-interventions'),
    
    # URL pour compléter le rapport d'intervention (terminer l'intervention et générer/télécharger le PDF)
    path('interventions/<int:pk>/complete-report/', CompleteInterventionReportView.as_view(), name='intervention-complete-report'),
    
    # URL pour créer une intervention (deux versions, avec et sans ID de réclamation dans l'URL)
    path('interventions/create/', CreateInterventionView.as_view(), name='create-intervention'),
    path('interventions/create/<int:reclamation_id>/', CreateInterventionView.as_view(), name='create-intervention-with-id'),
    
    # Inclure les routes du router pour les opérations CRUD standard
    path('', include(router.urls)),
]