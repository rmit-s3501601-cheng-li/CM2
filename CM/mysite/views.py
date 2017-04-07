from django.shortcuts import render
from rest_framework import viewsets,permissions,status
from models import MyUser
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


def home(request):
    return render(request, 'index.html')

@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def adduser(request):  
    adminKey=request.POST.get('adminkey', '')
    username= request.POST.get('username', '')
    password=request.POST.get('password', '')
    repeat_password = request.POST.get('repeat_password', '')
    if adminKey!='iamadministrator':
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        if password == '' or repeat_password == '':
            return HttpResponse(HTTP_400_BAD_REQUEST)
        elif password != repeat_password:
            return HttpResponse(HTTP_400_BAD_REQUEST)
        user=MyUser.objects.filter(username=request.POST.get('username', ''))
        if user is not None:
            return HttpResponse(HTTP_400_BAD_REQUEST)
        else:
            new_user=MyUser(username=request.POST.get('username', '')
                                ,password=request.POST.get('password', ''),
                                permission=request.POST.get('permission', ''))
            new_user.save()
            return HttpResponse(HTTP_200_OK)
   
    
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def login(request):  
    user=MyUser.objects.filter(username=request.POST.get('username', '')
                                ,password=request.POST.get('password', ''))
    if user is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        user=MyUser.objects.get(username=request.POST.get('username', ''))
        if user.permission==1:
            return Response({"adminkey":'iamadministrator'})
        else:
            return HttpResponse(HTTP_200_OK)
    
    
    
@api_view(http_method_names=['PUT'])  
@permission_classes((permissions.AllowAny,))  
def changePassword(request): 
    userName=request.data.get('username','')
    newpassword=request.data.get('password','')
    re_newpassword=request.data.get('re_password','')
    user=MyUser.objects.filter(username=userName)
    if user is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    if newpassword == '' or re_newpassword == '':
        return HttpResponse(HTTP_400_BAD_REQUEST)
    elif newpassword != re_newpassword:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        user=MyUser.objects.get(username=userName)
        user.password=newpassword
        user.save()
        return HttpResponse(HTTP_200_OK)
    

@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def getUserList(request):
    adminKey=request.POST.get('adminkey', '')
    if adminKey!='iamadministrator':
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        user_list=MyUser.objects.all().values_list('username')
        return Response(user_list)

@api_view(http_method_names=['DELETE'])
@permission_classes((permissions.AllowAny,))  
def deleteUser(request):
    adminKey=request.data.get('adminkey', '')
    userName=request.data.get('username','')
    if adminKey!='iamadministrator':
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        user=MyUser.objects.filter(username=userName)
        if user is None:
            return HttpResponse(HTTP_400_BAD_REQUEST)
        else:
            MyUser.objects.filter(username=userName).delete()
            return HttpResponse(HTTP_200_OK)
            



@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def upLoad(request):

    newFile =request.FILES.get('myfile', None) 
    path=request.POST.get('path', None)
    if newFile is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    elif path is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    
    fpath , fname = os.path.split(path)
    if os.path.exists(path) is False:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        os.remove(path)
        #need update database
        destination = open(os.path.join(fpath,newFile.name),'wb+')
        for chunk in newFile.chunks():     
            destination.write(chunk)   
        #update database
        destination.close()  
        return HttpResponse(HTTP_200_OK)


    #myFile =request.FILES['myfile']

@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def addFile(request):
    newFile =request.FILES.get('myfile', None)
    path=request.POST.get('path', None)
    if newFile is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    elif path is None:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    
    if os.path.exists(path) is False:
        return HttpResponse(HTTP_400_BAD_REQUEST)
    else:
        destination = open(os.path.join(path,newFile.name),'wb+')
        for chunk in newFile.chunks():     
            destination.write(chunk)   
        #update database
        destination.close()  
        return HttpResponse(HTTP_200_OK)
    

    


@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def downLoad(request):
    
    #Change local path when doing test
    fileName = basePath + request.data.get('path', '')
    def file_iterator(file, chunk_size = 512):
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
