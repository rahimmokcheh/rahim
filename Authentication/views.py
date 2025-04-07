from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from Superviseur.models import *
from .decorators import user_is_authenticated
from django.contrib.auth.decorators import login_required
from Authentication.decorators import user_is_superviseur
#-------------------login view -------------------
@user_is_authenticated
def log_in(request):
    if request.method == 'POST':
        formulaire = LoginForm(request.POST)
        if formulaire.is_valid(request):
            pseudo = formulaire.cleaned_data['pseudo']
            password = formulaire.cleaned_data['password']
            data = authenticate(request, username=pseudo, password=password)
            if data:
                login(request, data)
                request.session['user_pseudo'] = pseudo #enregistrement de pseudo dans la session pour l'utiliser dans le decorater
                if Client.objects.filter(pseudo=pseudo).exists():  
                    return redirect('dashboard_client')
                else :
                    return redirect('dashboard_superviseur')
                
        # Nous passons le formulaire au modèle même s'il n'est pas valide.
        return render(request, 'login.html', {'form': formulaire})
    else:
    # Nous passons le formulaire au modèle pour les requêtes GET.
        return render(request, 'login.html', {'form': LoginForm()})

#-------------------logout view -------------------
def logout_view(request):
    logout(request)
    return redirect('login')

#-------------------the other pages views -------------------
def error(request):
    return render(request, '404.html')

def superviseur_error(request):
    return render(request, 'superviseur_error.html')


def client_error(request):
    return render(request, 'client_error.html')

