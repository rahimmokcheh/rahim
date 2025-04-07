from django.urls import path
from . import views

urlpatterns = [

    #les 4 etapes pour la creation d'un nouveau client 
    path('ajout_client', views.ajout_client, name='ajout_client'),
    path('ajout_projet/<str:pseudo>', views.ajout_projet, name='ajout_projet'),
    path('ajout_zone/<str:name_project>', views.ajout_zone, name='ajout_zone'),
    path('ajout_cam/<str:name_project>', views.ajout_cam, name='ajout_cam'),

    #pages choix de redirection vers noveau client/client existant
    path('choix/', views.choix, name='choix'),
    path('handle-existing-client/', views.handle_existing_client, name='handle_existing_client'),
    path('client-existant/', views.select_existing_client, name='select_existing_client'),

    #pages de dashboard/stream/map/etc.... de la superviseur
    path('dashboard_superviseur', views.dashboard_superviseur, name='dashboard_superviseur'),
    path('map_superviseur', views.map_superviseur, name='map_superviseur'),
    path('stream_superviseur', views.stream_superviseur, name='stream_superviseur'),
    path('profile_superviseur', views.profile_superviseur, name='profile_superviseur'),

            #urls de la page stream_superviseur pour les selection des clients et les projets respectivement
        path('api/clients/', views.client_list, name='client_list'),
        path('api/projects/<str:client_pseudo>/', views.project_list, name='project_list'),
        path('api/cameras/<str:project_name>/', views.camera_list, name='camera_list'),
        path('video_feed/<str:cam_name>/', views.video_feed, name='video_feed'),

    ]
