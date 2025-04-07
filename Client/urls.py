from django.urls import include, path
from . import views

urlpatterns = [
    path('dashboard_client/', views.dashboard_client, name='dashboard_client'),
    path('map_client/', views.map_client, name='map_client'),
    path('stream_client/', views.stream_client, name='stream_client'),
    path('profile_client/', views.profile_client, name='profile_client'),
]

