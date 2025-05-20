# interventions/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AllInterventionsView,
    CompleteInterventionReportView,
    InterventionViewSet,
    OtherUsersInterventionsView,
    UserInterventionsView,
    CreateInterventionView,
    InterventionStatsView, # Import the new view
)

router = DefaultRouter()
router.register('interventions', InterventionViewSet)

urlpatterns = [
    path('interventions/user/<int:user_id>/', UserInterventionsView.as_view(), name='user-interventions'),
    path('interventions/<int:pk>/complete-report/', CompleteInterventionReportView.as_view(), name='intervention-complete-report'),
    path('interventions/create/', CreateInterventionView.as_view(), name='create-intervention'),
    path('interventions/create/<int:reclamation_id>/', CreateInterventionView.as_view(), name='create-intervention-with-id'),
    path('interventions/others/', OtherUsersInterventionsView.as_view(), name='other-users-interventions'),
    path('interventions/all/', AllInterventionsView.as_view(), name='all-interventions'),
    path('interventions/stats/', InterventionStatsView.as_view(), name='intervention-stats'), # New URL for statistics

    path('', include(router.urls)),
]