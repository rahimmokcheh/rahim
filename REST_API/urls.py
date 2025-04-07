from django.urls import path
from .views import *

urlpatterns = [
    path('api/', DetectionResult.as_view(), name='api'),
    path('apilogin/', ClientLoginAPIView.as_view(), name='apilogin'),
    path('apicam/<int:cameraName>/', get_camera_coordinates, name='get_camera_coordinates'),
    path('apizone/<int:cameraName>/', ZoneByProjet, name='zone'),

]
