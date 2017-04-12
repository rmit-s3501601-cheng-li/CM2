from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from models import MyUser,Registration_Request
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


def Homepage(request):
    return render(request, 'index.html')

@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def AddUser(request): 
    infor = json.loads(request.body)
    requestID = infor['requestID']
    try:
        registration = Registration_Request.objects.get(id=requestID)
        new_user=MyUser(username=registraton.username , 
                        password=registraton.password,
                        permission=registration.permission)
        new_user.save()
        return Response({'ststus':200})
    except:
        return Response({'ststus':400})
    

@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def Registory(request): 
    registration=json.loads(request.body)
    username=registration['username']
    password=registration['password']
    permission=registration['permission']
    comment=registration['comment']
    new_request=Registration_Request(Username=username,Password=password,
                                     Permission=permission,Comment=comment)
    new_request.save()
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

    
    
    
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def ChangePassword(request): 
    infor = json.loads(request.body)
    ID=infor['userId']
    password=infor['password']
    user = MyUser.objects.get(id=ID)
    user.password = password
    user.save()
    return Response({'status':200})
    

@api_view(http_method_names=['GET'])  
@permission_classes((permissions.AllowAny,))  
def GetRequestList(request):


    user_list = Registration_Request.objects.all().values_list('username', 'id','permission','comment')
              
    return Response(user_list)


@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def getUserDetail(request):

    infor = json.loads(request.body)
    ID=infor['userId']
    user=MyUser.objects.get(id=ID)
    
              
    return Response({'username':user.username})


@api_view(http_method_names=['DELETE'])
@permission_classes((permissions.AllowAny,))  
def DeleteUser(request):
    infor = json.loads(request.body)
    ID=infor['userId']
    user = MyUser.objects.get(id=ID).delete()
    return Response({'ststus':200})
            



@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def upLoad(request):

    newFile = request.FILES.get('myfile', None) 
    path = request.POST.get('path', None)
    if newFile is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    elif path is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    
    fpath , fname = os.path.split(path)
    if os.path.exists(path) is False:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        os.remove(path)
        # need update database
        destination = open(os.path.join(fpath, newFile.name), 'wb+')
        for chunk in newFile.chunks():     
            destination.write(chunk)   
        # update database
        destination.close()  
        return HttpResponse(HTTP_200_OK)


    # myFile =request.FILES['myfile']

@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def addFile(request):
    newFile = request.FILES.get('myfile', None)
    path = request.POST.get('path', None)
    if newFile is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    elif path is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    
    if os.path.exists(path) is False:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        destination = open(os.path.join(path, newFile.name), 'wb+')
        for chunk in newFile.chunks():     
            destination.write(chunk)   
        # update database
        destination.close()  
        return HttpResponse(HTTP_200_OK)
    

    


@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def downLoad(request):
    
    # Change local path when doing test
    fileName = basePath + request.data.get('path', '')
    def file_iterator(file, chunk_size=512):
        with open(file) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(fileName))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)

    return response
