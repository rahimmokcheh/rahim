from django.shortcuts import *
from .forms import *
from .models import *
from .mail_report import *
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.gis.geos import *
from django.contrib.auth.decorators import login_required
from Authentication.decorators import user_is_superviseur
from django.urls import reverse
import smtplib #smtp pour "simple mail transfer protocol" (pour l'envoie des mail aux clients)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .mail_report import send_email
import json
from datetime import datetime, timedelta
#-----------------------------------------on a essayé de commenter le code pour le rendre plus compréhensible-----------------
#---------------------------------dashboard_superviseur----------------------------
@login_required(login_url='login')
@user_is_superviseur
def dashboard_superviseur(request):
    Projets = Projet.objects.all() 

    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion
    if request.method == 'POST':
        client_name = request.POST.get('client_name')  
        project_name = request.POST.get('project_name')

        selected_project = Projet.objects.get(name_project=project_name)
        #filter emails of the selected client 
        client = get_object_or_404(Client, name_client=client_name)
        recipient_email = client.email
   
        # Calculate the datetime of 24 hours ago
        last_24_hours = datetime.now() - timedelta(hours=24)

        # Filter detection results based on the selected project and last 24 hours
        detection_results = DetectionResult.objects.filter(
            user__pseudo=client_name, 
            camera_name__name_project=selected_project,
            detected_at__gte=last_24_hours
        )
        #envoie email
        if 'send_email_button' in request.POST:
            if detection_results:
                send_email(recipient_email, detection_results)
    return render(request, 'dashboard_superviseur.html',{'Projets': Projets, 'appel_pseudo_superviseur':appel_pseudo_superviseur })

#----------------map_superviseur-------------------

@login_required(login_url='login')
def map_superviseur(request):
    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion
    # Récupère tous les clients.
    clients = Client.objects.all()
    # Vérifie si un client est choisi.
    selected_client_pseudo = request.GET.get('selected_client')
    # Et pour le projet, on regarde si y'a un choix.
    selected_project_name = request.GET.get('selected_project')
    zones, cams = [], []  # Prépare les listes pour zones et cams.
    # Filtre les projets par client, si un client est choisi.
    projects = Projet.objects.filter(pseudo__pseudo=selected_client_pseudo) if selected_client_pseudo else []
    if selected_project_name:
        # Trouve le projet sélectionné et ses zones/cams.
        selected_project = projects.filter(name_project=selected_project_name).first()
        zones = Zone.objects.filter(name_project=selected_project)
        cams = Cam.objects.filter(name_project=selected_project)
    # Retourne tout au template pour affichage.
    return render(request, 'map_superviseur.html', {
        'clients': clients,
        'projects': projects,
        'zones': zones,
        'cams': cams,
        'appel_pseudo_superviseur':appel_pseudo_superviseur,
    })

#---------------stream_superviseur--------------------
def stream_superviseur(request):
    appel_pseudo_superviseur = request.session.get('user_pseudo')

    return render(request, 'stream_superviseur.html', {'appel_pseudo_superviseur': appel_pseudo_superviseur})

#---------------profile_superviseur--------------------
@login_required(login_url='login')
@user_is_superviseur
def profile_superviseur(request):

    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion
    return render(request, 'profile_superviseur.html',{'appel_pseudo_superviseur':appel_pseudo_superviseur})

#-----------------------------les 4 etapes pour la creation d'un nouveau client------------------
#---------------ajout_client----------------
@login_required(login_url='login')
@user_is_superviseur
def ajout_client(request):
    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion
    if request.method == 'POST':
        form = ajout_client_Form(request.POST)
        if form.is_valid():
            name_client, gender, pseudo, email, phone_number, mot_de_passe, description_client = form.instance_client()
            donnees_client = Client(name_client=name_client, gender=gender, pseudo=pseudo, email=email, phone_number=phone_number, description_client=description_client)
            donnees_client.save()
            compte = User.objects.create_user(pseudo, email, mot_de_passe)
            compte.save()
            if email:
                    # Créer un message multipart
                    msg = MIMEMultipart('alternative')
                    msg['From'] = 'fireshield.s4g@gmail.com'
                    msg['To'] = email
                    msg['Subject'] = 'Bienvenue à votre Compte Fire Shield !'
                    # Ajouter le texte brut au message
                    text = 'Hello, click to validate'
                    part1 = MIMEText(text, 'plain')
                    msg.attach(part1)
                    # Ajouter le bouton au message en HTML
                    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        #container {{
            background-color: #ffffff;
            text-align: center;
            border-radius: 8px;
            overflow: hidden;
            margin: 2em auto;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            max-width: 700px;
        }}
        .product-details {{
            padding: 20px;
        }}
        .product-details h1 {{
            color: #333;
            font-size: 24px;
            margin-top: 0;
      }}
        .product-details h3 {{
            color: #666;
            font-size: 18px;
            font-weight: normal;
        }}
        .product-image img {{
            width: 100%;
            height: auto;
            border-bottom: 1px solid #eee;
       }}
        .btn {{
            display: inline-block;
            background-color: #4CAF50;
            color: #ffffff;
            padding: 10px 20px;
            font-size: 18px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            transition: background-color 0.3s;
        }}
        .btn:hover {{
            background-color: #45a049;
       }}
    </style>
</head>
<body>
    <div id="container">
        <div class="product-image">
            <img src="https://smartforgreen.com/wp-content/uploads/2023/07/featured_page.png" alt="Feature Image">
        </div>
        <div class="product-details">
            <h3>Bonjour {name_client}! Ci-joint vous trouvez vos informations d'identification pour votre compte Fire Shield</h3>
            <h2>Username: {pseudo}</h2>
            <h2>Mot de passe: {mot_de_passe}</h2>
            <a href="{request.build_absolute_uri(reverse('login'))}" class="btn">Se Connecter Ici</a>
        </div>
    </div>
</body>
</html>
                    '''
                    part2 = MIMEText(html, 'html')
                    msg.attach(part2)
                    # Envoyer le message e-mail
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login('fireshield.s4g@gmail.com','mhls spyc smlm tszb')
                        smtp.sendmail(msg['From'], msg['To'], msg.as_string())

            messages.success(request, 'Client crée avec succès !')
            messages.success(request, 'Un e-mail contenant les infos d"identification a été envoyé à votre client.')
            return redirect('ajout_projet', pseudo)  
    else:
        form = ajout_client_Form()

    return render(request, 'ajout_client.html', {'form': form,'appel_pseudo_superviseur':appel_pseudo_superviseur })

#--------------ajout_projet-----------------
@login_required(login_url='login')
@user_is_superviseur
def ajout_projet(request,pseudo):
    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion
    client_instance = Client.objects.get(pseudo=pseudo)
    if request.method == 'POST':
        form = ajout_projet_Form(request.POST)
        if form.is_valid():
            instance = form.instance_projet()
            name_project, ville, description_projet = instance

            données_projet = Projet(name_project=name_project, ville=ville, description_projet=description_projet ,pseudo=client_instance)
            données_projet.save()
            messages.success(request, 'Projet est ajouté avec succès !')
            return redirect('ajout_zone',name_project)  # Redirection vers la page suivant "zone"    
    else:
        form = ajout_projet_Form()

    return render(request, 'ajout_projet.html', {'form': form,'votre_client':pseudo, 'appel_pseudo_superviseur':appel_pseudo_superviseur})

#--------------ajout_zone----------------
@login_required(login_url='login')
@user_is_superviseur
def ajout_zone(request, name_project):
    Projet_instance = Projet.objects.get(name_project=name_project)
    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion
    if request.method == 'POST':
        name_zone=request.POST.get('name_zone')
        description_zone=request.POST.get('description')
        Multi_polygone= request.POST.get('coords_polys')
        ajoutez_un_polygone= request.POST.get('ajoutez_un_polygone')
        if ajoutez_un_polygone:
            zones=Zone.objects.filter(name_project=name_project)

            Instance_Multi_polygone = GEOSGeometry(Multi_polygone, srid=4326)
            données_zone=Zone(name_zone=name_zone, description_zone=description_zone, coords_polys=Instance_Multi_polygone, name_project=Projet_instance)
            données_zone.save()
            return render(request, 'ajout_zone.html',{'votre_projet':name_project, 'zones' : zones})
        else:
            Instance_Multi_polygone = GEOSGeometry(Multi_polygone, srid=4326)
            données_zone=Zone(name_zone=name_zone, description_zone=description_zone, coords_polys=Instance_Multi_polygone, name_project=Projet_instance)
            données_zone.save()
            
            messages.success(request, 'Vos Zones sont ajoutés avec succès !')
            return redirect('ajout_cam',name_project)  # Redirection vers la page suivant "zone"        
   
    return render(request, 'ajout_zone.html',{'votre_projet':name_project, 'appel_pseudo_superviseur':appel_pseudo_superviseur})

#--------------ajout_cam----------------
@login_required(login_url='login')
@user_is_superviseur
def ajout_cam(request, name_project):
    #n3ayet l 2esm l projet
    Projet_instance = Projet.objects.get(name_project=name_project)
    #n3ayett lel polygones l mawjoudin f projet en cours 
    zones=Zone.objects.filter(name_project=name_project)
    #appel de pseudo enrgistré dans la session lors de connexion
    appel_pseudo_superviseur = request.session.get('user_pseudo') 

    if request.method == 'POST':
        name_cam=request.POST.get('name_cam')
        adresse_cam=request.POST.get('adresse_cam')
        num_port=request.POST.get('num_port')
        rest_de_path=request.POST.get('rest_de_path')
        custom_url=request.POST.get('custom_url')
        description_cam=request.POST.get('description_cam')
        Multi_marker= request.POST.get('coords_cam')

        ajoutez_un_cam= request.POST.get('ajoutez_un_cam')

        if ajoutez_un_cam:
            #filtrage 7asb 2esm l projet (name_project cle etrangere f Cam )
            cams=Cam.objects.filter(name_project=name_project) 

            if custom_url :
                is_full_rtsp_url = True
            else:
                is_full_rtsp_url = False

            Instance_Multi_marker = GEOSGeometry(Multi_marker, srid=4326)
            données_cam=Cam(name_cam=name_cam,adresse_cam=adresse_cam, num_port=num_port,rest_de_path=rest_de_path,custom_url=custom_url,is_full_rtsp_url=is_full_rtsp_url,description_cam=description_cam, coords_cam=Instance_Multi_marker, name_project=Projet_instance)

            données_cam.save()

            return render(request, 'ajout_cam.html',{'votre_projet':name_project, 'zones' : zones, 'cams': cams})
        else:

            if custom_url :
                is_full_rtsp_url = True
            else:
                is_full_rtsp_url = False

            Instance_Multi_marker = GEOSGeometry(Multi_marker, srid=4326)
            données_cam=Cam(name_cam=name_cam,adresse_cam=adresse_cam, num_port=num_port,rest_de_path=rest_de_path,custom_url=custom_url,is_full_rtsp_url=is_full_rtsp_url,description_cam=description_cam, coords_cam=Instance_Multi_marker, name_project=Projet_instance)

            données_cam.save()

            messages.success(request, 'Vos Caméras sont bien ajoutée!')
            return redirect('login')  # Redirection vers la page suivant "zone" 
        
    return render(request, 'ajout_cam.html',{'votre_projet':name_project, 'zones' : zones,'appel_pseudo_superviseur':appel_pseudo_superviseur})


#--------------------------choix entre les clients existants ou creer un nouveau client ----------------------
@login_required(login_url='login')
@user_is_superviseur
def handle_existing_client(request):
    if request.method == 'POST':
        pseudo = request.POST.get('existing_client')
        # Redirigez l'utilisateur vers la page ajout_projet.html avec le pseudo du client sélectionné comme contexte
        return redirect('ajout_projet', pseudo=pseudo)
    else:
        # Gérer le cas où la méthode n'est pas POST
        return redirect(request, '404.html')

@login_required(login_url='login')
@user_is_superviseur
def select_existing_client(request):
    clients = Client.objects.values_list('pseudo', flat=True)
    appel_pseudo_superviseur = request.session.get('user_pseudo') #appel de pseudo enrgistré dans la session lors de connexion

    return render(request, 'select_existing_client.html', {'clients': clients, 'appel_pseudo_superviseur':appel_pseudo_superviseur})

@login_required(login_url='login')
@user_is_superviseur
def choix(request):
    return render(request, 'choix.html')


# Importation des modules Django nécessaires pour les vues et les réponses JSON
def client_list(request):
    # Récupération de la liste des clients sous forme de dictionnaires JSON
    clients = list(Client.objects.all().values('pseudo', 'name_client'))
    return JsonResponse(clients, safe=False)

def project_list(request, client_pseudo):
    # Récupération de la liste des projets pour un client donné
    projects = list(Projet.objects.filter(pseudo__pseudo=client_pseudo).values('name_project'))
    return JsonResponse(projects, safe=False)

def camera_list(request, project_name):
    # Récupération de la liste des caméras pour un projet donné
    cameras = list(Cam.objects.filter(name_project__name_project=project_name).values('name_cam', 'adresse_cam', 'num_port'))
    return JsonResponse(cameras, safe=False)

