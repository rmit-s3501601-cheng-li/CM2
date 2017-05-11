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
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import httplib2

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
    try:
        user=User.objects.filter(username=username)
        if user.exists() is False:
            user=Registration_Request.objects.filter(Username=username)
            if user.exists() is False:
                new_request=Registration_Request(Username=username,Password=password,Email=email,
                                     Permission=permission,Comment=comment)
                new_request.save()
                credentials = get_credentials()
                http = credentials.authorize(httplib2.Http())
                service = discovery.build('gmail', 'v1', http=http)
                SendMessage(service, "me", CreateMessage("ykd522@gmail.com", "ykd522@gmail.com", username + " want to join", username + ": " + comment))
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
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        SendMessage(service, "me", CreateMessage("ykd522@gmail.com", registration.Email, "Welcome to Chinese Medicine", registration.Username + " \nYou can login now"))
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
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        SendMessage(service, "me", CreateMessage("ykd522@gmail.com", registration.Email,  "Sorry", registration.Username + " \nYou are not allowed to login"))
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
        random_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        password = ''.join(random.sample(random_string,8))
        # password = '023459'
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
@permission_classes((permissions.AllowAny,)) 
def FirstSearch(request): 
    infor = json.loads(request.body)
    type=infor['type']
    keyword=infor['keyword']
    if type=='Title':
        book_list=book.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        other_list=others.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Type':
        book_list=book.objects.filter(file_type__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        other_list=others.objects.filter(file_type__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    elif type=='Study reference':
        book_list=book.objects.filter(study_reference=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        return Response(book_list)
    elif type=='Study id':
        book_list=book.objects.filter(study_ID__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        return Response(book_list)
    elif type=='All':
        if keyword =='':
            book_list=book.objects.all().values_list('id','file_type','titles','monograph_part','file_ownership')
            other_list=others.objects.all().values_list('id','file_type','titles','monograph_part','file_ownership')
        else:
            book_list=book.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
            other_list=others.objects.filter(titles__contains=keyword).values_list('id','file_type','titles','monograph_part','file_ownership')
        content = {
        'book_list': book_list,
        'other_list':other_list
        }
        return Response(content)
    else:
        return Response({'status':400})


@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def AdvancedSearchOr(request):
    infor=json.loads(request.body)
    type=infor['type']; #type list
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
        
        elif type[i]=='Study reference':
            book_list=book_list|book.objects.filter(study_reference=keyword[i])
            
        elif type[i]=='Study id':
            book_list=book_list|book.objects.filter(study_ID__contains=keyword[i])
            
        elif type[i]=='All':
            if keyword =='':
                book_list=book_list|book.objects.all()
                other_list=other_list|others.objects.all()
            else:
                book_list=book_list|book.objects.filter(titles__contains=keyword[i])
                other_list=other_list|others.objects.filter(titles__contains=keyword[i]) 
    content = {
            'book_list': book_list.values_list('id','file_type','titles','monograph_part','file_ownership'),
            'other_list':other_list.values_list('id','file_type','titles','monograph_part','file_ownership')
            }
    return Response(content)
    
@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def AdvancedSearchAnd(request):
    infor=json.loads(request.body)
    type=infor['type']; #type list
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
        
        elif type[i]=='Study reference':
            book_list= book_list.filter(study_reference=keyword[i])
            
        elif type[i]=='Study id':
            book_list= book_list.filter(study_ID__contains=keyword)
            
        elif type[i]=='All':
            if keyword =='':
                book_list= book_list.filter(titles__contains=keyword[i])
                other_list=other_list.filter(titles__contains=keyword[i])
            else:
                book_list= book_list.filter(titles__contains=keyword[i])
                other_list=other_list.filter(titles__contains=keyword[i])  
    content = {
            'book_list': book_list.values_list('id','file_type','titles','monograph_part','file_ownership'),
            'other_list':other_list.values_list('id','file_type','titles','monograph_part','file_ownership')
            }
    return Response(content)
    


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
    type = infor['type']
    # file=book.objects.get(id=bookID)
    # file.delete()
    # return Response({'status':200})
    if type =='pdf':
        file=book.objects.get(id=bookID)
    else:
        file=others.objects.get(id=bookID)
    path=file.path
    abso_path = '/Applications/XAMPP/htdocs' + path
    
    if os.path.exists(abso_path) is False:
        return Response({'status':400})
    else:
        os.remove(abso_path)
        # need update database
        
        file.delete()
        return Response({'status':200}) 
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
        
        
@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def EditFile(request):
    infor = json.loads(request.body)
    type=infor['type']
    fileID=infor['id']
    newFile = request.FILES['file'] 
    if newFile is None:
        return Response({'status':400}) 
    else:   
        if type =='pdf':
            file=book.objects.get(id=fileID)
        else:
            file=others.objects.get(id=fileID)
        path=file.path
        abso_path = '/Applications/XAMPP/htdocs' + path
        fpath , fname = os.path.split(path)
        if os.path.exists(abso_path) is False:
            return Response({'status':400})
        else:
            os.remove(abso_path)
            # need update database
            abso_path = '/Applications/XAMPP/htdocs' + fpath
            destination = open(os.path.join(abso_path, newFile.name), 'wb+')
            for chunk in newFile.chunks():     
                destination.write(chunk)   
            file.titles=newFile.name
            fpath = os.path.join(fpath, '', newFile.name)
            file.path=fpath
            file.save()
            destination.close()  
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

