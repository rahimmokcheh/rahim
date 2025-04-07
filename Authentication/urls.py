    
from django.urls import include, path
from . import views
urlpatterns = [
    #page login(duhhh!)
    path('login', views.log_in, name='login'),
    path('lougout', views.logout_view, name='logout'),
    
    #----------------error pages-------------------
    path('error', views.error, name='error'),
    path('superviseur_error', views.superviseur_error, name='superviseur_error'),
    path('client_error', views.client_error, name='client_error'),

]