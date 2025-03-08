from django.urls import path
from .views import ReclamationListCreateView, ReclamationDetailView, ReclamationListView
from .views import ReclamationByUserView
urlpatterns = [
    path('reclamations/', ReclamationListCreateView.as_view(), name='reclamation-list-create'),
    path('reclamations/<int:pk>/', ReclamationDetailView.as_view(), name='reclamation-detail'),
    path('', ReclamationListView.as_view(), name='list_reclamation'),
    path('reclamations/user/<int:user_id>/', ReclamationByUserView.as_view(), name='reclamations_by_user'),


]