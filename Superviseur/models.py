# Superviseur/models.py
from django.contrib.gis.db import models
from django.db.models import JSONField
from django.core.exceptions import ValidationError

#--------------------------Model Superviseur---------------------------
class Superviseur(models.Model):
    GENDER_CHOICES = [
        ('', '-'),
        ('M', 'Male'),
        ('F', 'Femelle'),
        ('O', 'Organization'),  
    ]
    name_superviseur = models.CharField( null=True)
    pseudo = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)  
    email = models.EmailField(null=True, unique= True)
    phone_number = models.BigIntegerField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True) 
    description_superviseur = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.pseudo
    #pour tester choix du genre dans les tests
    def clean(self):
        super().clean()
        if self.gender not in dict(self.GENDER_CHOICES).keys():
            raise ValidationError({'gender': 'Invalid gender choice'})
#--------------------------Model Client---------------------------
class Client(models.Model):
    GENDER_CHOICES = [
        ('', '-'),
        ('M', 'Male'),
        ('F', 'Femelle'),
        ('O', 'Organization'),  
    ]
    name_client = models.CharField(null=True)
    pseudo = models.CharField(primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)  
    email = models.EmailField(null=True)
    phone_number = models.BigIntegerField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True) 
    description_client = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name_client}"

#----------------------------Model projet-------------------------
class Projet(models.Model):
    name_project = models.CharField(max_length=20, primary_key=True)
    ville = models.CharField(null=True)
    contrat_picture = models.ImageField(upload_to='contract_pics/', null=True,blank=True) #optionnel
    description_projet = models.TextField(null=True, blank=True)
    pseudo=models.ForeignKey(Client,on_delete=models.CASCADE)

    def __str__(self):
        return f"Projet '{self.name_project}' De la Client {self.pseudo}"  
    
#--------------Model Zone--------------------------
class Zone(models.Model):
    name_zone = models.CharField(max_length=100, primary_key=True)
    coords_polys = models.MultiPolygonField(null=True)
    description_zone = models.TextField(null=True, blank=True)
    name_project=models.ForeignKey(Projet,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name_zone} Du Projet {self.name_project}"  
    
#--------------Model Cam--------------------------- 
class Cam(models.Model):

    cam_ID=models.AutoField(primary_key=True)
    name_cam = models.CharField(max_length=20)
    coords_cam = models.PointField(null=True)
    adresse_cam = models.GenericIPAddressField(null=True, blank=True)  # Now optional and used for IP-based streams
    num_port = models.CharField(null=True, blank=True)  # Also optional and used for IP-based streams
    rest_de_path=models.CharField(null=True, blank=True)
    description_cam = models.TextField(null=True, blank=True)
    custom_url = models.TextField(null=True, blank=True)  # Custom validator is used here    is_full_rtsp_url = models.BooleanField(default=False)  # Indicates which stream type is being used
    is_full_rtsp_url = models.BooleanField(default=False)  # Indicates stream type
    name_project = models.ForeignKey(Projet, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name_cam} Du {self.name_project}"
    
   #-----------------------------Model Resultas des Detection---------------------------
class DetectionResult(models.Model):

    camera_name = models.ForeignKey(Cam, on_delete=models.CASCADE,null=True)#chaque detection est attribué à son camera
    user = models.ForeignKey(Client, on_delete=models.CASCADE,null=True)#chaque detection est attribué à son client
    detection_data = JSONField(null=True)
    path_to_image=models.CharField(null=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Résultat des détection pour ({self.camera_name}) Detecté à ({self.detected_at})"



