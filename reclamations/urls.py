from django.urls import path
from .views import (
    ReclamationListCreateView,
    ReclamationDetailView,
    ReclamationByUserView
)  # Supprimé l'importation en double et `ReclamationListView` s'il n'existe pas

urlpatterns = [
    path('reclamations/', ReclamationListCreateView.as_view(), name='reclamation-list-create'),
    path('reclamations/<int:pk>/', ReclamationDetailView.as_view(), name='reclamation-detail'),
    path('reclamations/user/<int:user_id>/', ReclamationByUserView.as_view(), name='reclamations_by_user'),
]

