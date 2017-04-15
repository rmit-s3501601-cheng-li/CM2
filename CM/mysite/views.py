from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from django.db.models.query import QuerySet
from rest_framework.views import APIView
from django.template.context_processors import request
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from django.http.response import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import json
from models import Registration_Request,UserProfile
from django.contrib.auth.models import User




@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))
@csrf_exempt  
def Register(request): 
    registration=json.loads(request.body)
    username=registration['username']
    password=registration['password']
    permission=registration['permission']
    email=registration['email']
    comment=registration['comment']
    try:
        new_request=Registration_Request(Username=username,Password=password,email=email,
                                     Permission=permission,Comment=comment)
        new_request.save()
        return Response({'ststus':200})
    except:
        return Response({'ststus':400})


@api_view(http_method_names=['POST'])  
@permission_classes((permissions.IsAuthenticated,))  
def AddUser(request): 
    infor = json.loads(request.body)
    requestID = infor['requestID']  
    registration = Registration_Request.objects.get(id=requestID)
    new_user=User.objects.create_user(username=registration.Username,password=registration.Password,email=registration.Email)
    new_user.save()
    new_user=User.objects.get(id=new_user.id)
    new_user.userprofile.permission=registration.Permission
    new_user.save()
    return Response({'ststus':200})
    
    
    
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def Login(request):  
    infor = json.loads(request.body)
    user = MyUser.objects.filter(username=infor['username'])
    if user.exists() is True :
        user = user.filter(password=infor['password'])
        if user.exists() is True :
            loguser = MyUser.objects.get(username=infor['username'])
            if loguser.permission == 1:
                return Response({'status':200, 'permission':loguser.permission, 'adminkey':'iamadministrator'})
            else:
                return Response({'status':200, 'permission':loguser.permission})
    return Response({'status':400})
