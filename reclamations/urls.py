from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReclamationCreateView,
    ReclamationDetailView,
    ReclamationListView,
    ReclamationFilterView,
    ReclamationStatisticsView,
    ReclamationPCViewSet,
    ReclamationElectriqueViewSet,
    ReclamationDiversViewSet
)

# Router pour les viewsets
router = DefaultRouter()
router.register('reclamations-pc', ReclamationPCViewSet)
router.register('reclamations-electrique', ReclamationElectriqueViewSet)
router.register('reclamations-divers', ReclamationDiversViewSet)

urlpatterns = [
    # URLs pour les réclamations
    path('create/', ReclamationCreateView.as_view(), name='reclamation-create'),
    path('<int:pk>/', ReclamationDetailView.as_view(), name='reclamation-detail'),
    path('', ReclamationListView.as_view(), name='reclamation-list'),
    path('filter/', ReclamationFilterView.as_view(), name='reclamation-filter'),
    path('statistics/', ReclamationStatisticsView.as_view(), name='reclamation-statistics'),
    
    # Inclure les routes du router
    path('viewsets/', include(router.urls))
]