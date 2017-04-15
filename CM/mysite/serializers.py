from models import Registration_Request
from django.contrib.auth.models import User
from rest_framework import serializers


        
class RequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Registration_Request
        fields = ( 'id','username','email''permission','comment')