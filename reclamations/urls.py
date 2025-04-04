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
    ReclamationDiversViewSet,
    UserReclamationsView,
    ReclamationsEnAttenteView,
    ReclamationsEnCoursView,
    ReclamationsTermineesView,
    DeleteReclamationView,
    UserReclamationsByStatusView

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
    

    path('user/<int:user_id>/', UserReclamationsView.as_view(), name='user-reclamations'),
    path('status/en-attente/', ReclamationsEnAttenteView.as_view(), name='reclamations-en-attente'),
    path('status/en-cours/', ReclamationsEnCoursView.as_view(), name='reclamations-en-cours'),
    path('status/terminees/', ReclamationsTermineesView.as_view(), name='reclamations-terminees'),
    path('delete/<int:reclamation_id>/', DeleteReclamationView.as_view(), name='delete-reclamation'),
    path('user/<int:user_id>/status/<str:status>/', UserReclamationsByStatusView.as_view(), name='user-reclamations-status'),

    # Inclure les routes du router
    path('viewsets/', include(router.urls))
]