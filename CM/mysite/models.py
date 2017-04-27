from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from unittest.util import _MAX_LENGTH
from django.template.defaultfilters import default
from django.db.models.signals import post_save

# Create your models here.
class UserProfile(models.Model):
    user =  models.OneToOneField(User)
    permission = models.IntegerField(null=True)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile()
        profile.user = instance
        profile.save()
              
post_save.connect(create_user_profile, sender=User)

    
class Registration_Request(models.Model):
    Username=models.CharField(max_length=15,null=False)
    Password=models.CharField(max_length=20,null=False)
    Permission=models.IntegerField(default=3,null=False)
    Email=models.CharField(max_length=25,null=False)
    Comment=models.CharField(max_length=50,null=True)
    
class others(models.Model):
    titles = models.CharField(max_length=100,null=False)
    file_type = models.CharField(max_length=100,null=False)
    path=models.CharField(max_length=100,null=False)
    file_ownership=models.CharField(max_length=100,null=False)
    modification_time=models.CharField(max_length=100,null=False)
    monograph_part=models.CharField(max_length=100,null=False)
    
    
class book(models.Model): 
    study_reference =models.CharField(max_length=100)
    monograph_part =models.CharField(max_length=100)
    Intervention= models.CharField(max_length=100)
    study_design=models.CharField(max_length=100)
    study_ID=models.CharField(max_length=100)   
    titles =models.CharField(max_length=100)
    file_type=models.CharField(max_length=100)
    path=models.CharField(max_length=100)
    file_ownership=models.CharField(max_length=100)
    modification_time=models.CharField(max_length=100)
    #reference=models.CharField(max_length=100)
    

    
    
