from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # API Users
    path('api/reclamations/', include('reclamations.urls')),
    path('reset-password/', include('PasswordResetToken.urls')),
    path('api/', include('gestion.urls')),  # Inclure les URLs de l'application gestion


]

# Ajout de la gestion des fichiers médias en dehors de la liste urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
