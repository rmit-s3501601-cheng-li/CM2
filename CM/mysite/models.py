from tastypie.utils.timezone import now
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from unittest.util import _MAX_LENGTH
from django.template.defaultfilters import default

# Create your models here.
class MyUser(models.Model):
    username = models.CharField(max_length=15)
    password=models.CharField(max_length=20)
    permission = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    
