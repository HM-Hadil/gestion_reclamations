from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Importez vos vues existantes ici
    InterventionViewSet,
    UserInterventionsView,
    FinirInterventionView,
    GenererRapportView
)

# Router pour les viewsets
router = DefaultRouter()
# Ajoutez vos autres viewsets ici
router.register('interventions', InterventionViewSet)

urlpatterns = [
    # Vos URLs existantes ici
    
    # URLs pour les interventions
    path('interventions/user/<int:user_id>/', UserInterventionsView.as_view(), name='user-interventions'),
    path('interventions/<int:intervention_id>/terminer/', FinirInterventionView.as_view(), name='terminer-intervention'),
    path('interventions/rapport/', GenererRapportView.as_view(), name='generer-rapport'),
    
    # Inclure les routes du router
    path('', include(router.urls))
]