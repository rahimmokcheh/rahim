from django.urls import include, path
from . import views
urlpatterns = [
    
    path('', views.Home, name='Home'),
    path('Home', views.Home, name='Home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('services', views.services, name='services'),
    path('monotoriat', views.monotoriat, name='monotoriat'),
    path('protect_f', views.protect_forest, name='protect_f'),


    
    ]
