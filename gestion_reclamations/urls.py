from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Create a schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version='v1',
        description="Your API Description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # API Users
    path('api/reclamations/', include('reclamations.urls')),
    path('reset-password/', include('PasswordResetToken.urls')),
    path('api/', include('gestion.urls')),  # Include URLs for gestion app
    path('api/', include('Intervention.urls')),
    
    # Add the Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
]

# Adding static media files management when in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
