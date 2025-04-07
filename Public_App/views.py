from django.shortcuts import *

#---------------Public_App View-------------
def Home(request):
    return render(request, 'Home.html')

def contact(request):
    return render(request, 'contact.html')

def services(request):
    return render(request, 'services.html')

def protect_forest(request):
    return render(request, 'protect_f.html')

def monotoriat(request):
    return render(request, 'monotoriat.html')

def about(request):
    return render(request, 'about.html')

#---------------Public_App View-------------