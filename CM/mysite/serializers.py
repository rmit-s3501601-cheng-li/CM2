from models import Registration_Request
from django.contrib.auth.models import User
from models import book
from rest_framework import serializers


        
class RequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Registration_Request
        fields = ( 'id','username','email''permission','comment')
        
class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=book
        fields=('id','titles','file_type')