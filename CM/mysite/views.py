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
        book_list=book.objects.filter(file_type__contains=keyword).values_list('id','titles','monograph_part','file_ownership')
        other_list=others.objects.filter(file_type__contains=keyword).values_list('id','titles','monograph_part','file_ownership')
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
    
    
@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def add(request):
    
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Himaya 2012 Paeonol from Hippocampus kuda Bleeler suppressed',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Bai shao and chi shao/Himaya 2012 Paeonol from Hippocampus kuda Bleeler suppressed.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save() 
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Nam 2013 Paeoniflorin a monoterpene glycoside attenuates LPS',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Bai shao and chi shao/Nam 2013 Paeoniflorin a monoterpene glycoside attenuates LPS.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Wang 2014 Comparative studies of paeoniflorin and albiflorin from Paeonia lactiflora on anti inflammatory',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Bai shao and chi shao/Wang 2014 Comparative studies of paeoniflorin and albiflorin from Paeonia lactiflora on anti inflammatory.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Yu 2007 Antinociceptive effects of systemic paeoniflorin on',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Bai shao and chi shao/Yu 2007 Antinociceptive effects of systemic paeoniflorin on.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Zhang 2013 Synergistic interaction between TGP and TFL on chronic constriction injury',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Bai shao and chi shao/Zhang 2013 Synergistic interaction between TGP and TFL on chronic constriction injury.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Raphael 2003 CHAI HU Immunomodulatory activity of naturally occurring monoterpenes',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chai hu/Raphael 2003 CHAI HU Immunomodulatory activity of naturally occurring monoterpenes.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Schulz 1997 CHAI HU Perillic acid inhibits Ras_MAPkinase-driven',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chai hu/Schulz 1997 CHAI HU Perillic acid inhibits Ras_MAPkinase-driven.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Yoon 2010 CHAI HU Limonene suppresses lipopolysaccharide-induced production',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chai hu/Yoon 2010 CHAI HU Limonene suppresses lipopolysaccharide-induced production.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Zhou 2014 Attenuation of neuropathic pain by saikosaponin a ',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chai hu/Zhou 2014 Attenuation of neuropathic pain by saikosaponin a .pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Calixto-Campos 2015 Vanillic acid inhibits inflammatory pain by inhibiting neutrophil',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chuan xiong/Calixto-Campos 2015 Vanillic acid inhibits inflammatory pain by inhibiting neutrophil.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Danthi 2004 Caffeic acid esters activate TREK-1 potassium channels NOT USED',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chuan xiong/Danthi 2004 Caffeic acid esters activate TREK-1 potassium channels NOT USED.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Lampiasi 2016 The molecular events behind ferulic acid mediated modulation of IL-6',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chuan xiong/Lampiasi 2016 The molecular events behind ferulic acid mediated modulation of IL-6.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Li 2016 a-Pinene, linalool and 1-octanol contribute to the topical antiinflammatory',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chuan xiong/Li 2016 a-Pinene, linalool and 1-octanol contribute to the topical antiinflammatory.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Xiao 2015 Ligustilide treatment promotes functional recovery in a rate model of SCI NOT USED',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Chuan xiong/Xiao 2015 Ligustilide treatment promotes functional recovery in a rate model of SCI NOT USED.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Cao 2015 Tanshinone IIA attenuates neuropathic pain via inhibiting glial',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dan shen/Cao 2015 Tanshinone IIA attenuates neuropathic pain via inhibiting glial.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Cherng 2014 Baicalin ameliorates neuropathic pain by suppressing HDAC1 expresison',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dan shen/Cherng 2014 Baicalin ameliorates neuropathic pain by suppressing HDAC1 expresison.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Isacchi 2011 Salvianolic acid B and its liposomal formulations',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dan shen/Isacchi 2011 Salvianolic acid B and its liposomal formulations.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Beaudry 2010 Pharmacokinetics vanillin hypersensitivity neuropath rats PhytotherRes 24(4) p525-30',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dang gui/Beaudry 2010 Pharmacokinetics vanillin hypersensitivity neuropath rats PhytotherRes 24(4) p525-30.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Chen 2010 Assmt immunoregulatory Angelica in vitro macrophages Intl Immunopharm 10 p422-30',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dang gui/Chen 2010 Assmt immunoregulatory Angelica in vitro macrophages Intl Immunopharm 10 p422-30.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Fu 2011 Lipopolysaccharide n-butylidenephthalide Biotechnol Lett 33 p903-10',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dang gui/Fu 2011 Lipopolysaccharide n-butylidenephthalide Biotechnol Lett 33 p903-10.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Su 2011 Ligustilide prevent LPSinduced iNOS expression Intl Immunopharm 11 p1166-72',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dang gui/Su 2011 Ligustilide prevent LPSinduced iNOS expression Intl Immunopharm 11 p1166-72.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Yang 2007 Macrophage activation acidic polysacc JBiochemMolBio 40(5) p636-43',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Dang gui/Yang 2007 Macrophage activation acidic polysacc JBiochemMolBio 40(5) p636-43.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Chen 2014 Liquiritigenin alleviates mechanical and cold hyperalgesia',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Gan cao/Chen 2014 Liquiritigenin alleviates mechanical and cold hyperalgesia.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Guenette 2007 Pharmacokinetics of eugenol and its effects on thermal hypersensitivity in rats',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Guenette 2007 Pharmacokinetics of eugenol and its effects on thermal hypersensitivity in rats.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Choi 2007 Oral administration of acqueous extract of carthami flos CELLULAR IMMUNITY',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Hong hua/Choi 2007 Oral administration of acqueous extract of carthami flos CELLULAR IMMUNITY.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Liao 2014 Effect of honghua (flos cathami) on NO production',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Hong hua/Liao 2014 Effect of honghua (flos cathami) on NO production.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Lv 2015 Hydroxysafflor yellow A exerts neuroprotective effects in cerebral ischemia NOT USED',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Hong hua/Lv 2015 Hydroxysafflor yellow A exerts neuroprotective effects in cerebral ischemia NOT USED.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Lv 2016 Hydroxysafflor yellow a attenuates neuron damage',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Hong hua/Lv 2016 Hydroxysafflor yellow a attenuates neuron damage.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Tien 2010 Carthamus tinctorius L prevents LPS induced TNFa signaling activation and cell apoptosis NOT USED',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Hong hua/Tien 2010 Carthamus tinctorius L prevents LPS induced TNFa signaling activation and cell apoptosis NOT USED.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Chen 2014 Phenolic derivatives from Radix Astragali ABSTRACT ONLYNOT USED',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Huang qi/Chen 2014 Phenolic derivatives from Radix Astragali ABSTRACT ONLYNOT USED.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Lai 2014 Anti-inflammatory activities of an active fraction',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Huang qi/Lai 2014 Anti-inflammatory activities of an active fraction.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Li 2014 Flavanoids from Astragalus membranaceus and their inhibitory effects on LPS',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Huang qi/Li 2014 Flavanoids from Astragalus membranaceus and their inhibitory effects on LPS.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Ryu 2008 Astragali radix elicits antiinflammation via activation',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Huang qi/Ryu 2008 Astragali radix elicits antiinflammation via activation.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Wei 2016 TLR-4 may mediate signaling pathways of Astragalus',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Huang qi/Wei 2016 TLR-4 may mediate signaling pathways of Astragalus.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    new_book = book(study_reference='NA',monograph_part='PHN',Intervention='NA',study_ID='NA',titles='Zhang 2015 Astragaloside IV inhibits NF-Kb activation',file_type='pdf',path='/Herpes zoster/Experimental studies/PHN experimental evidence/Huang qi/Zhang 2015 Astragaloside IV inhibits NF-Kb activation.pdf',file_ownership='Experimental studies',modification_time='2017-04-24 16:05:46',study_design='NA')
    new_book.save()
    return Response({'status':200})

        
    
    


