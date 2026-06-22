from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from accounts.views import ProfileView

def health(_request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health, name='health'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('companies.urls')),
    path('api/', include('analysis.urls')),
]
