# Superviseur/forms.py
from django import forms
from .models import *
from django.contrib.auth.models import User


#----------------------------------------ajout_client_Form---------------------------------------------------------------------------------------
class ajout_client_Form(forms.Form):

    name_client = forms.CharField( widget=forms.TextInput(attrs={'id':"name_client", 'name': "name_client", 'class': "form-control rounded", 'placeholder':"Nom Client / Organisation" }))
    pseudo = forms.CharField( widget=forms.TextInput(attrs={'id':"pseudo", 'name': "pseudo", 'class': "form-control rounded", 'placeholder':"Pseudo" }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'email', 'name': 'email', 'placeholder': 'E-Mail', 'class': "form-control rounded"}))
    mot_de_passe = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'id': 'password', 'name': 'password', 'placeholder': 'Mot de passe', 'class': "form-control rounded"}))
    confirmation_mot_de_passe = forms.CharField(required=True,widget=forms.PasswordInput (attrs={'id': 'confirm_password', 'name': 'confirm_password', 'placeholder': 'Re-saisir le Mot de Passe', 'class': "form-control rounded"}))
    gender = forms.ChoiceField(choices=Client.GENDER_CHOICES, widget=forms.Select(attrs={'id': "gender", 'name': "gender",'class': 'form-select', 'aria-label': 'Genre'}))
    description_client = forms.CharField(widget=forms.Textarea(attrs={'id':"description_client", 'name': "description_client", 'class': "form-control rounded", 'placeholder':"Description de Client",'style':"height: 100px;" }))
    phone_number = forms.IntegerField(widget=forms.TextInput(attrs={'id':"phone_number", 'name': "phone_number", 'class': "form-control rounded", 'placeholder':"Num de Téléphone"}))

    def is_valid(self):
        pseudo = self.data['pseudo']
        if Client.objects.filter(pseudo=pseudo).exists() or User.objects.filter(username=pseudo).exists():
            self.add_error("pseudo", "Pseudo déja existant !")

        email = self.data['email']
        if User.objects.filter(email=email).exists():
            self.add_error("email", "Ce mail déja existant !")

        phone_number = self.data['phone_number']
        if len(phone_number) != 8 or not phone_number.isdigit():
            self.add_error("phone_number", "Le numéro de téléphone doit se composer de 8 chiffres!")

        mot_de_passe = self.data['mot_de_passe'] 
        if len(mot_de_passe) < 8:
            self.add_error("mot_de_passe", "Le mot de passe doit contenir au moins 8 caractères !")

        confirmation_mot_de_passe = self.data['confirmation_mot_de_passe']
        if confirmation_mot_de_passe != mot_de_passe:
            self.add_error("confirmation_mot_de_passe","Les mots de passe ne sont pas correspondants !")

        value = super(ajout_client_Form,self).is_valid()
        return value
    
    def instance_client(self):
        name_client = self.data['name_client']
        gender = self.data['gender']
        pseudo = self.data['pseudo']
        email = self.data['email']
        phone_number=self.data['phone_number']
        mot_de_passe = self.data['mot_de_passe']
        description_client = self.data['description_client']
        return name_client, gender, pseudo, email, phone_number, mot_de_passe, description_client

#-------------------------ajout_projet_Form  ---------------------

class ajout_projet_Form(forms.Form):
    name_project=forms.CharField( widget=forms.TextInput(attrs={'id':"name_project", 'name': "name_project", 'class': "form-control rounded", 'placeholder':"Nom de Projet" }))
    ville=forms.CharField( widget=forms.TextInput(attrs={'id':"ville", 'name': "ville", 'class': "form-control rounded", 'placeholder':"Ville" }))
    description_projet= forms.CharField(widget=forms.Textarea(attrs={'id':"description_projet", 'name': "description_projet", 'class': "form-control rounded", 'placeholder':"Description de Projet",'style':"height: 100px;" }))
        
    def is_valid(self):
        name_project = self.data['name_project']
        if Projet.objects.filter(name_project=name_project).exists() :
            self.add_error("name_project", "Le client déja posséde un projet avec ce Nom !")

        name_project = self.data['name_project'] 
        if len(name_project) > 20:
            self.add_error("name_project", "Le nom de projet ne doit passer 20 Caractéres !")

        value = super(ajout_projet_Form,self).is_valid()
        return value
    
    def instance_projet(self):
        name_project = self.data['name_project']
        ville = self.data['ville']
        description_projet = self.data['description_projet']
        
        return name_project, ville, description_projet

