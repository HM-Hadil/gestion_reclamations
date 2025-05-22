from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AllReclamationsFilterView,
    PCsByLaboratoireView,  # Remplace EquipementsByLaboratoireView
    ReclamationCreateView,
    ReclamationDetailView,
    ReclamationListView,
    ReclamationFilterView,
    ReclamationStatisticsView,
    ReclamationPCViewSet,
    ReclamationElectriqueViewSet,
    ReclamationDiversViewSet,
    UserReclamationsView,
    ReclamationsEnAttenteView,
    ReclamationsEnCoursView,
    ReclamationsTermineesView,
    DeleteReclamationView,
    UserReclamationsByStatusView,
    AnalyseStatistiqueView,
    CreatePCView,
    PCDetailView,
    PCListView,
    ReclamationsByPCView,
    StatistiquesPCView,
    LaboratoireListView
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
    path('analyse-statistique/', AnalyseStatistiqueView.as_view(), name='analyse-statistique'),
    path('reclamations/all_filtered/', AllReclamationsFilterView.as_view(), name='all-reclamations-filtered'),

    # URLs pour les PCs (remplace les équipements)
    path('laboratoires/<int:laboratoire_id>/pcs/', PCsByLaboratoireView.as_view(), name='pcs-by-laboratoire'),
    path('pcs/create/', CreatePCView.as_view(), name='create-pc'),
    path('pcs/<int:pk>/', PCDetailView.as_view(), name='pc-detail'),
    path('pcs/', PCListView.as_view(), name='pc-list'),
    path('pcs/<int:pc_id>/reclamations/', ReclamationsByPCView.as_view(), name='reclamations-by-pc'),
    path('pcs/statistics/', StatistiquesPCView.as_view(), name='statistiques-pc'),
    
    # URLs pour les laboratoires
    path('laboratoires/', LaboratoireListView.as_view(), name='laboratoire-list'),

    # URLs pour les réclamations par utilisateur et statut
    path('user/<int:user_id>/', UserReclamationsView.as_view(), name='user-reclamations'),
    path('status/en-attente/', ReclamationsEnAttenteView.as_view(), name='reclamations-en-attente'),
    path('status/en-cours/', ReclamationsEnCoursView.as_view(), name='reclamations-en-cours'),
    path('status/terminees/', ReclamationsTermineesView.as_view(), name='reclamations-terminees'),
    path('delete/<int:reclamation_id>/', DeleteReclamationView.as_view(), name='delete-reclamation'),
    path('user/<int:user_id>/status/<str:status>/', UserReclamationsByStatusView.as_view(), name='user-reclamations-status'),

    # Inclure les routes du router
    path('viewsets/', include(router.urls))
]