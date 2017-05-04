from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from django.db.models.query import QuerySet
from rest_framework.views import APIView
from django.template.context_processors import request
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes
from django.core.files.storage import FileSystemStorage
import os
import json
from models import Registration_Request,UserProfile,book,others
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse, StreamingHttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from serializers import BookSerializer





@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))
def Register(request): 
    registration=json.loads(request.body)
    username=registration['username']
    password=registration['password']
    permission=registration['permission']
    email=registration['email']
    comment=registration['comment']
    try:
        user=User.objects.filter(username=username)
        if user.exists() is False:
            user=Registration_Request.objects.filter(Username=username)
            if user.exists() is False:
                new_request=Registration_Request(Username=username,Password=password,Email=email,
                                     Permission=permission,Comment=comment)
                new_request.save()
                return Response({'ststus':200})
            else:
                return Response({'ststus':400})
        else:
            return Response({'ststus':400})
    except:
        return Response({'ststus':400})


@api_view(http_method_names=['POST'])  
@permission_classes((permissions.IsAdminUser,))  
def AcceptRequest(request): 
    infor = json.loads(request.body)
    requestID = infor['requestID'] 
    try: 
        registration = Registration_Request.objects.get(id=requestID)
        new_user=User.objects.create_user(username=registration.Username,password=registration.Password,email=registration.Email)
        new_user.save()
        new_user=User.objects.get(username=new_user.username)
        new_user.userprofile.permission=registration.Permission
        new_user.userprofile.save()
        registration.delete()
        return Response({'ststus':200})
    except:
        return Response({'ststus':400})
        
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.IsAdminUser,))  
def RejectRequest(request): 
    infor = json.loads(request.body)
    requestID = infor['requestID']
    try: 
        registration = Registration_Request.objects.get(id=requestID)
        registration.delete()
        return Response({'ststus':200})
    except:
        return Response({'ststus':400})


@api_view(http_method_names=['POST'])  
@permission_classes((permissions.IsAdminUser,))  
def AddAdminUser(request): 
    infor = json.loads(request.body)
    username=infor['username']
    password=infor['password']
    email=infor['email']
    try:
        user=User.objects.filter(username=username)
        if user.exists() is True:
            return Response({'ststus':400})
        else:
            new_user=User.objects.create_superuser(username,email,password)
            new_user.save()
            new_user=User.objects.get(username=new_user.username)
            new_user.userprofile.permission=1     
            new_user.userprofile.save()
            return Response({'ststus':200})
    except:
        return Response({'ststus':400})
    
    
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def Login(request):  
    infor = json.loads(request.body)
    username=infor['username']
    password=infor['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        return Response({'status':200, 'permission':user.userprofile.permission})
    else:
        return Response({'status':400})


@api_view(http_method_names=['GET'])  
@permission_classes((permissions.IsAdminUser,))  
def GetRequestList(request):
    try:
        user_list = Registration_Request.objects.all().values_list('id','Username','Permission','Comment','Email')
        return Response(user_list)
    except:
        return Response({'status':400})
    


@api_view(http_method_names=['GET'])  
@permission_classes((permissions.IsAuthenticated,))  
def ChangePassword(request):
    infor = json.loads(request.body)
    password=infor['password']
    userID=infor['userID']
    try:
        user=User.objects.get(id=userID)
        user.set_password(password)
        user.save()
        return Response({'status':200})
    except:
        return Response({'status':400})
    
    
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))
def ForgetPassword(request): 
    infor = json.loads(request.body)
    username=infor['username']
    try:
        user=User.objects.get(username=username)
        email=user.email
        return Response({'status':200})
    except:
        return Response({'status':400})
    


@api_view(http_method_names=['POST'])   
@permission_classes((permissions.AllowAny,)) 
def FirstSearch(request): 
    infor = json.loads(request.body)
    type=infor['type']
    keyword=infor['keyword']
    page=infor['page']
    if type=='Title':
        book_list=book.objects.filter(titles__contains=keyword).values_list('id','titles','monograph_part','file_ownership', 'path')
        other_list=others.objects.filter(titles__contains=keyword).values_list('id','titles','monograph_part','file_ownership', 'path')
        content = {
        'book_list': books.object_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Type':
        book_list=book.objects.filter(file_type=keyword).values_list('id','titles','monograph_part','file_ownership')
        other_list=others.objects.filter(file_type=keyword).values_list('id','titles','monograph_part','file_ownership')
        paginator = Paginator(book_list, 2)
        books = paginator.page(page)
        content = {
        'book_list': books.object_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Study reference':
        book_list=book.objects.filter(study_reference=keyword).values_list('id','titles','monograph_part','file_ownership')
        return Response(book_list)
    elif type=='Study id':
        book_list=book.objects.filter(study_ID__contains=keyword).values_list('id','titles','monograph_part','file_ownership')
        return Response(book_list)
    elif type=='All':
        book_list=book.objects.all().values_list('id','titles','monograph_part','file_ownership')
        other_list=others.objects.all().values_list('id','titles','monograph_part','file_ownership')
        content = {
        'book_list': books.object_list,
        'other_list':other_list
        }
        return Response(content)    
    else:
        return Response({'status':400})
    
    
        
        
        
        

@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))
def ViewFile(request): 
    infor = json.loads(request.body)
    bookID=infor['id']
    file=book.objects.get(id=bookID)
    return Response({'path':file.path})   
    # path = '/Users/kaidiyu/Desktop' + file.path
    # data = open("/Users/kaidiyu/Desktop/a1pg.pdf", "rb").read()
    # return HttpResponse(data)

    
    
    
    
    
    
@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def download(request):

    infor = json.loads(request.body)
    bookID=infor['id']
    file=book.objects.get(id=bookID)
    return Response({'path':file.path}) 
    # path = '/Users/kaidiyu/Desktop' + file.path
    # # fileName = basePath + request.data.get('path', '')
    # def file_iterator(file, chunk_size = 512):
    #     with open(file) as f:
    #         while True:
    #             c = f.read(chunk_size)
    #             if c:
    #                 yield c
    #             else:
    #                 break

    # response = StreamingHttpResponse(file_iterator(path))
    # response['Content-Type'] = 'application/octet-stream'
    # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file.path)

    # return response 


@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def DeleteFile(request):
    infor = json.loads(request.body)
    bookID=infor['id']
    file=book.objects.get(id=bookID)
    file.delete()
    return Response({'status':200})



@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def GetFileDetail(request):
    infor = json.loads(request.body)
    type=infor['type']
    fileID=infor['id']
    if type=='pdf':
        file=book.objects.get(id=fileID)
        contents={
            'id':file.id,
            'title': file.titles,
            'category':file.monograph_part,
            'studyReference':file.study_reference,
            'studyID':file.study_ID,
            'monograph':file.file_ownership,
            'intervention':file.Intervention,
            'fileType':file.file_type,
            'modification':file.modification_time
            }
        return Response(contents)
    else:
        file=others.objects.get(id=fileID)
        contents={
            'id':file.id,
            'title':file.titles,
            'category':file.monograph_part,
            'fileType':file.file_type,
            'monograph':file.file_ownership,
            'modification':file.modification_time
            }
        return Response(contents)
        
        
@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def EditFile(request):
    infor = json.loads(request.body)
    type=infor['type']
    fileID=infor['id']
    newFile = request.FILES.get('myfile', None) 
    if newFile is None:
        pass
        
    if type =='pdf':
        file=book.objects.get(id=fileID)
    else:
        file=others.objects.get(id=fileID)
    path=file.path
    fpath , fname = os.path.split(path)
    if os.path.exists(path) is False:
        return Response({'status':400})
    else:
        os.remove(path)
        # need update database
        destination = open(os.path.join(fpath, newFile.name), 'wb+')
        for chunk in newFile.chunks():     
            destination.write(chunk)   
        # update database
        destination.close()  
        return Response({'status':200})
        
    
    


