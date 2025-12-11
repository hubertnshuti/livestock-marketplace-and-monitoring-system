"""
URL configuration for livestock_backend project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import home, for_farmers, for_buyers, about, contact

# --- API SETUP ---
from rest_framework.routers import DefaultRouter
from livestock import api_views # Import the new API views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'livestock', api_views.LivestockViewSet)
router.register(r'species', api_views.SpeciesViewSet)
# -----------------

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # HTML / TEMPLATE ROUTES
    path('livestock/', include('livestock.urls', namespace='livestock')), 
    path("accounts/", include("accounts.urls")),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('for-farmers/', for_farmers, name='for_farmers'),
    path('for-buyers/', for_buyers, name='for_buyers'),
    path('contact/', contact, name='contact'),
    
    # API ROUTES (http://127.0.0.1:8000/api/livestock/)
    path('api/', include(router.urls)),
    
    # API Login helper (optional but good for testing)
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)