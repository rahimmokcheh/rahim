#d'authentification
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
#-------------------------Login_Form  ---------------------
class LoginForm(forms.Form):
    pseudo = forms.CharField(required=True, widget=forms.TextInput(attrs={'id': 'pseudo','name': 'pseudo','class': "form-control rounded",'placeholder': 'Pseudo',}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'id': 'password','name': 'password','placeholder': 'Mot de passe','class': "form-control rounded"}) )
    
    def is_valid(self, request):
        pseudo = self.data['pseudo']
        password = self.data['password']
        if User.objects.filter(username=pseudo).exists():
            user = authenticate(request, username=pseudo,password=password)
            if user is None:
                self.add_error("password", "Mot de Passe incorrect !")
        else:
            self.add_error("pseudo", "Ce compte n'existe pas !")
        return super(LoginForm, self).is_valid()
