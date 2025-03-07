from django.urls import path

from users import UserUpdateView
from .views import RegisterView, LoginView, UserDetailView, UserUpdateView  

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'), 
    path('user/update/<int:id>/', UserUpdateView.as_view(), name='update_user'),

]
