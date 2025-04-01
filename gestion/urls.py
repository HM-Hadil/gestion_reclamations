from django.urls import path
from .views import (
    SalleListCreateView, SalleDetailView,
    LaboratoireListCreateView, LaboratoireDetailView,
    BureauListCreateView, BureauDetailView
)
from .views import PCListCreateView, PCDetailView
urlpatterns = [
    # URLs pour Salle
    path('salles/', SalleListCreateView.as_view(), name='salle-list-create'),
    path('salles/<int:pk>/', SalleDetailView.as_view(), name='salle-detail'),

    # URLs pour Laboratoire
    path('laboratoires/', LaboratoireListCreateView.as_view(), name='laboratoire-list-create'),
    path('laboratoires/<int:pk>/', LaboratoireDetailView.as_view(), name='laboratoire-detail'),

    # URLs pour Bureau
    path('bureaux/', BureauListCreateView.as_view(), name='bureau-list-create'),
    path('bureaux/<int:pk>/', BureauDetailView.as_view(), name='bureau-detail'),

      # Liste et création des PC
    path('pc/', PCListCreateView.as_view(), name='pc-list-create'),
    # Détail, mise à jour et suppression d'un PC
    path('pc/<int:pk>/', PCDetailView.as_view(), name='pc-detail'),
]
