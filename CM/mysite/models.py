from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from unittest.util import _MAX_LENGTH
from django.template.defaultfilters import default
from django.db.models.signals import post_save

# Create your models here.
class UserProfile(models.Model):
    user =  models.OneToOneField(User)
    permission = models.IntegerField(default=3,null=True)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile()
        profile.user = instance
        profile.save()
              
post_save.connect(create_user_profile, sender=User)

    
class Registration_Request(models.Model):
    Username=models.CharField(max_length=15)
    Password=models.CharField(max_length=20)
    Permission=models.IntegerField(default=3)
    Email=models.CharField(max_length=25)
    Comment=models.CharField(max_length=50)
    

    
    
