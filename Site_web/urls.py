from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', include('Client.urls')),
    path('', include('Superviseur.urls')),
    path('', include('Public_App.urls')),
    path('', include('Authentication.urls')),
    path('', include('REST_API.urls')),
]
