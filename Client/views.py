from django.shortcuts import render
from Superviseur.models import *
from django.contrib.auth.decorators import login_required
from Authentication.decorators import user_is_client
from Superviseur.mail_report import *

@login_required(login_url='login')
@user_is_client
def dashboard_client(request):
    pseudo = request.session.get('user_pseudo')
    projets = Projet.objects.filter(pseudo__pseudo=pseudo)
    return render(request, 'dashboard_client.html', {'projets': projets,'pseudo':pseudo})


@login_required(login_url='login')
@user_is_client
def map_client(request):
    pseudo = request.session.get('user_pseudo')
    projects = Projet.objects.filter(pseudo__pseudo=pseudo)

    # Récupérer le projet sélectionné depuis les données de la requête
    selected_project_name = request.GET.get('selected_project')

    # Si un projet est sélectionné, filtrer les zones uniquement pour ce projet
    if selected_project_name:
        selected_project = projects.filter(name_project=selected_project_name).first()
        zones = Zone.objects.filter(name_project=selected_project)
        cams = Cam.objects.filter(name_project=selected_project)
    else:
        # Si aucun projet n'est sélectionné, ne pas filtrer les zones et afficher la carte vide
        zones = []
        cams = []
    # Passer les projets et les zones filtrées à votre modèle HTML
    return render(request, 'map_client.html', {'projects': projects, 'zones': zones, 'cams':cams,'pseudo':pseudo})


@login_required(login_url='login')
@user_is_client
def stream_client(request):
    pseudo = request.session.get('user_pseudo')
    return render(request, 'stream_client.html',{'pseudo':pseudo})



@login_required(login_url='login')
@user_is_client
def profile_client(request):
    pseudo = request.session.get('user_pseudo')
    return render(request, 'profile_client.html',{'pseudo':pseudo})


