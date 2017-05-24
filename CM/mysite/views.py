# -*- coding: utf-8 -*-
from rest_framework import viewsets, permissions, status
from django.template.context_processors import request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.core.files.storage import FileSystemStorage
import os
import json
from models import Registration_Request,UserProfile,book,others,log
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse, StreamingHttpResponse
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import random
import time
import httplib2
import shutil

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors


SCOPES = 'https://www.googleapis.com/auth/gmail.compose'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'




@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))
def Register(request): 

    registration=json.loads(request.body)
    username=registration['username']
    password=registration['password']
    permission=registration['permission']
    email=registration['email']
    comment=registration['comment']
    firstName=registration['first']
    lastName=registration['last']
    try:
        user=User.objects.filter(username=username)
        if user.exists() is False:
            user=Registration_Request.objects.filter(Username=username)
            if user.exists() is False:
                new_request=Registration_Request(Username=username,Password=password,Email=email,
                                     Permission=permission,Comment=comment,Firstname=firstName,Lastname=lastName)
                new_request.save()
                credentials = get_credentials()
                http = credentials.authorize(httplib2.Http())
                service = discovery.build('gmail', 'v1', http=http)
                SendMessage(service, "me", CreateMessage("ykd522@gmail.com", "ykd522@gmail.com", username + " want to join", username + ": " + comment))
                return HttpResponse(status.HTTP_200_OK)
            else:
                return HttpResponse(status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status.HTTP_400_BAD_REQUEST)
    except:
        return HttpResponse(status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def AcceptRequest(request): 
    infor = json.loads(request.body)
    requestID = infor['requestID'] 
    try: 
        registration = Registration_Request.objects.get(id=requestID)
        new_user=User.objects.create_user(username=registration.Username,password=registration.Password,
                                          email=registration.Email,first_name=registration.Firstname,last_name=registration.Lastname)
        new_user.save()
        new_user=User.objects.get(username=new_user.username)
        new_user.userprofile.permission=registration.Permission
        if registration.Permission==2:
            new_user.is_staff=True
            new_user.is_active=True
            new_user.is_superuser=False
        else:
            new_user.is_active=True
            new_user.is_staff=False
            new_user.is_superuser=False
        new_user.save()
        new_user.userprofile.save() 
        registration.delete()  
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        SendMessage(service, "me", CreateMessage("ykd522@gmail.com", registration.Email, "Welcome to Chinese Medicine", "Welcome" + registration.Username + " \n\nYou can login now."))  
        return HttpResponse(status.HTTP_200_OK)  
    except:
        return HttpResponse(status.HTTP_400_BAD_REQUEST)
        
@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def RejectRequest(request): 
    infor = json.loads(request.body)
    requestID = infor['requestID']   
    try: 
        registration = Registration_Request.objects.get(id=requestID)
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        SendMessage(service, "me", CreateMessage("ykd522@gmail.com", registration.Email,  "Sorry", registration.Username + " \n\nYou are not allowed to login"))
        registration.delete()
        return Response({'ststus':200})
    except:
        return Response({'ststus':400})


@api_view(http_method_names=['POST'])  
@permission_classes((permissions.AllowAny,))  
def AddAdminUser(request): 
    infor = json.loads(request.body)
    username=infor['username']
    password=infor['password']
    email=infor['email']
    first_name=infor['first']
    last_name=infor['last']
    try:
        user=User.objects.filter(username=username)
        if user.exists() is True:
            return Response({'ststus':400})
        else:
            new_user=User.objects.create_superuser(username=username,email=email,password=password,first_name=first_name,last_name=last_name)
            new_user.save()
            new_user=User.objects.get(username=new_user.username)
            new_user.userprofile.permission=1     
            new_user.userprofile.save()
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('gmail', 'v1', http=http)
            SendMessage(service, "me", CreateMessage("ykd522@gmail.com", email,  "Welcome " + username, "You can login now"))
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
    


@api_view(http_method_names=['POST'])  
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
        random_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        password = ''.join(random.sample(random_string,8))
        user.set_password(password)
        user.save()
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        SendMessage(service, "me", CreateMessage("ykd522@gmail.com", email, "Reset Password", username + '\n\nHere is your new password: ' + password))
        return Response({'status':200})
    except:
        return Response({'status':400})
    


@api_view(http_method_names=['POST'])   
@permission_classes((permissions.IsAuthenticated,)) 
def SimpleSearch(request): 
    infor = json.loads(request.body)
    type=infor['type']
    keyword=infor['keyword']
    if type=='Title':
        book_list=book.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        other_list=others.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='File Type':
        book_list=book.objects.filter(file_type__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        other_list=others.objects.filter(file_type__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Study Ref':
        book_list=book.objects.filter(study_reference=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        return Response(book_list)
    elif type=='Study ID':
        book_list=book.objects.filter(study_ID__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        return Response(book_list)
    elif type=='Intervention':
        book_list=book.objects.filter(Intervention=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        return Response(book_list)
    elif type=='Category':
        book_list=book.objects.filter(file_ownership__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        other_list=others.objects.filter(file_ownership__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Monograph':
        book_list=book.objects.filter(monograph_part=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        other_list=others.objects.filter(monograph_part=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Study design':
        book_list=book.objects.filter(study_design=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        return Response(book_list)
    elif type=='File path':
        book_list=book.objects.filter(path__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        other_list=others.objects.filter(path__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='All':
        if keyword =='':
            book_list=book.objects.all().values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
            other_list=others.objects.all().values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        else:
            book_list=book.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
            other_list=others.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    else:
        return Response({'status':400})


@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def AdvancedSearchOr(request):
    infor=json.loads(request.body)
    type=infor['type']
    keyword=infor['keyword']
    book_list=book.objects.filter(titles="")
    other_list=others.objects.filter(titles="")
    for i in range(len(keyword)):
        if type[i]=='Title':
            book_list= book_list|book.objects.filter(titles__contains=keyword[i])
            other_list=other_list|others.objects.filter(titles__contains=keyword[i])
        elif type[i]=='File Type':
            book_list=book_list|book.objects.filter(file_type__contains=keyword[i])
            other_list=other_list|others.objects.filter(file_type__contains=keyword[i])
        
        elif type[i]=='Study Ref':
            book_list=book_list|book.objects.filter(study_reference=keyword[i])
            
        elif type[i]=='Study id':
            book_list=book_list|book.objects.filter(study_ID__contains=keyword[i])
        
        elif type[i]=='Intervention':
            book_list=book_list|book.objects.filter(Intervention=keyword[i])
        elif type[i]=='Category':
            book_list=book_list|book.objects.filter(file_ownership__contains=keyword[i])
            other_list=other_list|others.objects.filter(file_ownership__contains=keyword[i])
        elif type[i]=='Monograph':
            book_list=book_list|book.objects.filter(monograph_part=keyword[i])
            other_list=other_list|others.objects.filter(monograph_part=keyword[i])
        elif type[i]=='Study design':
            book_list=book_list|book.objects.filter(study_design=keyword[i])
        elif type[i]=='File path':
            book_list=book_list|book.objects.filter(path__contains=keyword[i])
            other_list=other_list|others.objects.filter(path__contains=keyword[i])
        elif type[i]=='All':
            if keyword =='':
                book_list=book_list|book.objects.all()
                other_list=other_list|others.objects.all()
            else:
                book_list=book_list|book.objects.filter(titles__contains=keyword[i])
                other_list=other_list|others.objects.filter(titles__contains=keyword[i])
    content = {
            'book_list': book_list.values_list('id','file_type','titles','monograph_part','file_ownership','modification_time'),
            'other_list':other_list.values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
            }
    return Response(content)
    
    
    
@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def AdvancedSearchAnd(request):
    infor=json.loads(request.body)
    type=infor['type']
    keyword=infor['keyword']
    book_list=book.objects.filter()
    other_list=others.objects.filter()
    for i in range(len(keyword)):
        if type[i]=='Title':
            book_list= book_list.filter(titles__contains=keyword[i])
            other_list=other_list.filter(titles__contains=keyword[i])
        elif type[i]=='File Type':
            book_list= book_list.filter(file_type__contains=keyword[i])
            other_list=other_list.filter(file_type__contains=keyword[i])
        
        elif type[i]=='Study Ref':
            book_list= book_list.filter(study_reference=keyword[i])
            other_list=other_list.filter(titles="")
            
        elif type[i]=='Study id':
            book_list= book_list.filter(study_ID__contains=keyword[i])
            other_list=other_list.filter(titles="")
        elif type[i]=='Intervention':
            book_list= book_list.filter(Intervention=keyword[i])
            other_list=other_list.filter(titles="")
        elif type[i]=='Category':
            book_list=book_list.filter(file_ownership__contains=keyword[i])
            other_list=other_list.filter(file_ownership__contains=keyword[i])
        elif type[i]=='Monograph':
            book_list=book_list.filter(monograph_part=keyword[i])
            other_list=other_list.filter(monograph_part=keyword[i])
        elif type[i]=='Study design':
            book_list= book_list.filter(study_design=keyword[i])
            other_list=other_list.filter(titles="")
        elif type[i]=='File path':
            book_list=book_list.filter(path__contains=keyword[i])
            other_list=other_list.filter(path__contains=keyword[i])
        elif type[i]=='All':
            if keyword =='':
                pass
            else:
                book_list= book_list.filter(titles__contains=keyword[i])
                other_list=other_list.filter(titles__contains=keyword[i])  
    content = {
            'book_list': book_list.values_list('id','file_type','titles','monograph_part','file_ownership','modification_time'),
            'other_list':other_list.values_list('id','file_type','titles','monograph_part','file_ownership','modification_time')
            }
    return Response(content)
    
    
    
    


@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def ViewFile(request):
    infor = json.loads(request.body)
    bookID=infor['id']
    try:
        file=book.objects.get(id=bookID)
        return Response({'path':file.path})
    except :
        return HttpResponse(status.HTTP_400_BAD_REQUEST)
    # path = '/Users/kaidiyu/Desktop' + file.path
    # data = open("/Users/kaidiyu/Desktop/a1pg.pdf", "rb").read()
    # return HttpResponse(data)







@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def download(request):
    infor = json.loads(request.body)
    bookID=infor['id']
    try:
        file=book.objects.get(id=bookID)
        return Response({'path':file.path}) 
    except:
        return HttpResponse(status.HTTP_400_BAD_REQUEST)
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
@permission_classes((permissions.IsAuthenticated,))
def DeleteFile(request):
    infor = json.loads(request.body)
    bookID=infor['id']
    type = infor['type']
    userID=infor['userID']
    user=User.objects.get(id=userID)
    current=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    if type =='pdf':
        file=book.objects.get(id=bookID)
    else:
        file=others.objects.get(id=bookID)
    if type=='pdf':
        newLog=log(logType='Delete',titles=file.titles,user=user.username,file_type=file.file_type,path=file.path,
               file_ownership=file.file_ownership,modification_time=current,monograph_part=file.monograph_part,
               study_reference=file.study_reference,Intervention=file.Intervention,study_design=file.study_design,
               study_ID=file.study_ID)
    else:
        newLog=log(logType='Delete',titles=file.titles,user=user.username,file_type=file.file_type,path=file.path,
               file_ownership=file.file_ownership,modification_time=current,monograph_part=file.monograph_part)
    abso_path = '/Applications/XAMPP/htdocs' + file.path
    dest_path='/Applications/XAMPP/htdocs'+'/Bin'
    
    if os.path.exists(abso_path) is False:
        return Response({'status':400})
    else:
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        SendMessage(service, "me", CreateMessage("ykd522@gmail.com", registration.Email,  "File Delete Notification", file.titles + " \n\nDeleted.Check details in the log page"))
        shutil.move(abso_path, dest_path)       
        file.delete()
        newLog.save()
        return Response({'status':200})
    
    
@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def RecoveryFile(request):
    infor=json.loads(request.body)
    logID=infor['logID']
    file=log(id=logID)
    current=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    abso_path = '/Applications/XAMPP/htdocs' + file.path
    dest_path='/Applications/XAMPP/htdocs'+'/Bin'
    if file.file_type=='pdf':
        new_file=book(titles=file.titles,file_type=file.file_type,path=file.path,
               file_ownership=file.file_ownership,modification_time=current,monograph_part=file.monograph_part,
               study_reference=file.study_reference,Intervention=file.Intervention,study_design=file.study_design,
               study_ID=file.study_ID)
        
    else:
        new_fil=others(titles=file.titles,file_type=file.file_type,path=file.path,
               file_ownership=file.file_ownership,modification_time=current,monograph_part=file.monograph_part)
    new_file.save()        
    shutil.move(dest_path, abso_path)     
    return Response({'status':200})
        

    
    
    
    
    


@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def GetFileDetail(request):
    infor = json.loads(request.body)
    type=infor['type']
    fileID=infor['id']
    try:
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
                'modification':file.modification_time,
                'path':file.path
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
                'modification':file.modification_time,
                'path':file.path
                }
            return Response(contents)
    except:
        return HttpResponse(status.HTTP_400_BAD_REQUEST)
        
        


@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def EditFile(request): 
    newFile = request.FILES['file'] 
    type = request.POST.get('type')
    id = request.POST.get('id')
    userID=request.POST.get('userID')
    current=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    if newFile is None:
        return Response({'status':400}) 
    else:   
        if type =='pdf':
            file=book.objects.get(id=id)
        else:
            file=others.objects.get(id=id)
        user=User.objects.get(id=userID)
        newLog=log(logType='Edit',titles=file.titles,user=user.username,file_type=file.file_type,path=file.path,
                   file_ownership=file.file_ownership,modification_time=current,monograph_part=file.monograph_part)
        path=file.path
        abso_path = '/Applications/XAMPP/htdocs' + path
        fpath , fname = os.path.split(path)
        if os.path.exists(abso_path) is False:
            return Response({'status':400})
        else:
            os.remove(abso_path)
            abso_path = '/Applications/XAMPP/htdocs' + fpath
            destination = open(os.path.join(abso_path, newFile.name), 'wb+')
            for chunk in newFile.chunks():     
                destination.write(chunk)   
            file.titles=newFile.name
            fpath = os.path.join(fpath, '', newFile.name)
            file.path=fpath    
            file.modification_time=current
            file.save()
            newLog.save()
            destination.close()  
            return Response({'status':200})



@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def AddFile(request): 
    newFile = request.FILES['file'] 
    type = request.POST.get('type')
    title=request.POST.get('title')
    category=request.POST.get('category')
    monograph=request.POST.get('monograph')
    path='/Applications/XAMPP/htdocs'+'/newFile/'+title
    current=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    userID=request.POST.get('userID')
    user=User.objects.get(id=userID)
    if type=='pdf':
        reference=request.POST.get('study reference')
        intervention=request.POST.get('Intervention')
        design=request.POST.get('study design')
        ID=request.POST.get('study ID')
        file=book(titles=title,file_type=type,path=path,file_ownership=category,modification_time=current,
                  monograph_part=monograph,study_reference=reference,Intervention=intervention,study_design=design,study_ID=ID)
    
    else:
        file=others(titles=title,file_type=type,path=path,
                    file_ownership=category,modification_time=current,monograph_part=monograph)
    file.save()
    destination = open(path, 'wb+')
    for chunk in newFile.chunks():     
        destination.write(chunk)
    newLog=log(logType='Add',titles=title,user=user.username,file_type=type,path=path,
                   file_ownership=category,modification_time=current,monograph_part=monograph)
    newLog.save()    
    return Response({'status':200})





@api_view(http_method_names=['GET'])  
@permission_classes((permissions.IsAdminUser,))  
def GetLogList(request):
    try:
        logs_list = log.objects.all().values_list('id','logType','titles','user','modification_time')
        return Response(logs_list)
    except:
        return HttpResponse(status=400)
        



@api_view(http_method_names=['GET'])
@permission_classes((permissions.IsAdminUser,))
def GetUserList(request):  
    users=User.objects.all().values_list('id','username','email','is_superuser','is_staff','is_active')
    return Response(users)
     




@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAdminUser,))
def DeleteUser(request):  
    infor= json.loads(request.body)
    userID=infor['userID']
    user=User.objects.get(id=userID)
    user.delete()
    return Response({'status':200})
    



@api_view(http_method_names=['GET'])  
@permission_classes((permissions.IsAdminUser,))  
def GetRequestListCount(request):
    try:
        request_count = Registration_Request.objects.all().count()
        return Response(request_count)
    except:
        return Response({'status':400})





def SendMessage(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print 'Message Id: %s' % message['id']
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def CreateMessage(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sendEmail.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials