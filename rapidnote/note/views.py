from django.shortcuts import render, redirect
from .models import Member, FileSystem, FileList, HashList
from django.contrib import auth
from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import Q
from datetime import datetime
import math
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import response

# Create your views here.

def main(request):
    return redirect('note:login')


def myPage(request):
    return render(request, 'note/myPage.html')


def findIdPw(request):
    return render(request, 'note/findIdPw.html')


def viewer(request, id, task, memo):
    data=requestDB(id, task, memo)
    return render(request, 'note/viewer.html',data)

def download(request):
    return render(request, 'note/download.html')


def login(request):
    if request.method == 'POST':

        id = request.POST.get('user_id')
        password = request.POST.get('password')
        member_exist = Member.objects.filter(Q(member_id=id) & Q(pw=password))
        if member_exist:
            request.session['user_id'] = id
            return index(request)
        else:
            messages.info(request, '아이디 또는 비밀번호가 일치하지 않습니다.')
            return render(request, 'note/login.html')
    else:
        return render(request, 'note/login.html')


def signup(request):
    if request.method == "GET":
        return render(request, 'note/signup.html')
    else:
        id = request.POST.get('user_id', None)
        password = request.POST.get('password', None)
        mname = request.POST.get('user_name', None)
        mail = request.POST.get('user_mail', None)

        Member(member_id=id, pw=password, name=mname, email=mail).save()
        new_fileSystem = FileSystem(member_id=id, filePath="untitled", fileName="untitled",
                                    lastModifiedDate=timezone.localtime())
        new_fileSystem.save()
        insertDefault(new_fileSystem)

        return redirect('note:login')


def logout(request):
    auth.logout(request)
    return redirect('note:login')


def index(request):
    id = request.session['user_id']
    # 계정내 모든 파일 삭제하면 자동으로 디폴트 생성
    if not FileSystem.objects.filter(member_id=id):
        new_fileSystem = FileSystem(member_id=id, filePath="untitled", fileName="untitled",
                                    lastModifiedDate=timezone.localtime())
        new_fileSystem.save()
        insertDefault(new_fileSystem)

    file = FileSystem.objects.filter(member_id=id).order_by('-lastModifiedDate').first()
    url = "/" + file.filePath + "/" + file.fileName + "/"
    return redirect(url)


def idcheck(request):
    id = request.POST['user_id']
    if Member.objects.filter(member_id=id).exists():
        data = "unavailable"
    else:
        data = "available"
    return HttpResponse(data)


def insertDB(request):
    data = request.POST['msg']
    id = request.session['user_id']
    filepath = request.session['filepath']
    filename = request.session['filename']

    file = FileSystem.objects.get(member_id=id, filePath=filepath, fileName=filename)
    file.lastModifiedDate = timezone.localtime()
    file.save()

    leftdata = str(data).split("@@")[0]
    rightdata = str(data).split("@@")[1]
    leftseg = len(leftdata) / 3500
    print(leftseg)
    rightseg = len(rightdata) / 3500
    print(rightseg)
    FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=filepath + "/" + filename + "/")).delete()

    for i in range(0, math.ceil(leftseg)):
        new_fileList = FileList(member_id=id, fileName=filepath + "/" + filename + "/left" + str(i),
                                fileContent=leftdata[i * 3500:(i * 3500) + 3500])
        new_fileList.save()

    for i in range(0, math.ceil(rightseg)):
        new_fileList = FileList(member_id=id, fileName=filepath + "/" + filename + "/right" + str(i),
                                fileContent=rightdata[i * 3500:(i * 3500) + 3500])
        new_fileList.save()

    HashList.objects.filter(member_id=id, filePath=filepath, fileName=filename).delete()

    data = "저장되었습니다."
    return HttpResponse(data)


def requestDB(id, filepath, filename):
    filelist = FileList.objects \
        .filter(Q(member_id=id) & Q(fileName__startswith=filepath + "/" + filename + "/left")) \
        .order_by("fileName")
    leftdata = ""
    for f in filelist:
        leftdata = leftdata + f.fileContent

    rightdata = ""
    filelist = FileList.objects \
        .filter(Q(member_id=id) & Q(fileName__startswith=filepath + "/" + filename + "/right")) \
        .order_by("fileName")
    for f in filelist:
        rightdata = rightdata + f.fileContent

    data = {'leftdata': leftdata,
            'rightdata': rightdata}

    return data


def insertDefault(new_file):
    new_content_left = '<div id="memoTemp">' \
                       '<div id="groupCount" value="0" style="display: none;"></div>' \
                       '<div id="blockCount" value="0" style="display: none;"></div>' \
                       '<div id="grid" class="grid clearfix"></div> <!-- grid end --></div> ' \
                       '<!-- memoTemp end -->'
    new_fileList = FileList(member_id=new_file.member_id,
                            fileName=str(new_file.filePath + "/" + new_file.fileName + "/left0")
                            , fileContent=new_content_left)
    new_fileList.save()
    new_content_right = '<div id="memoFinal" name="memoFinal" contenteditable="false"></div> <!-- memoFinal end -->'
    new_fileList = FileList(member_id=new_file.member_id,
                            fileName=str(new_file.filePath + "/" + new_file.fileName + "/right0")
                            , fileContent=new_content_right)
    new_fileList.save()


# task 추가
def plustask(request):
    id = request.session['user_id']
    filepath = request.POST['filepath']

    if filepath.find("/") != -1:
        data = "unavailable"
        return HttpResponse(data)

    elif FileSystem.objects.filter(member_id=id, filePath=filepath).exists():
        data = "duplicated"
        return HttpResponse(data)

    else:
        new_fileSystem = FileSystem(member_id=id, filePath=filepath, fileName="untitled",
                                    lastModifiedDate=timezone.localtime())
        new_fileSystem.save()
        insertDefault(new_fileSystem)

        pathlist = FileSystem.objects.filter(member_id=id).values('filePath').distinct().order_by('filePath')
        context = {'pathlist': pathlist}

        return render(request, 'note/task.html', context)


# memo 추가
def plusmemo(request):
    id = request.session['user_id']
    filepath = request.POST['filepath']
    filename = request.POST['filename']

    if filename.find("/") != -1:
        data = "unavailable"
        return HttpResponse(data)

    elif FileSystem.objects.filter(member_id=id, filePath=filepath, fileName=filename).exists():
        data = "duplicated"
        return HttpResponse(data)

    else:
        new_fileSystem = FileSystem(member_id=id, filePath=filepath, fileName=filename,
                                    lastModifiedDate=timezone.localtime())
        new_fileSystem.save()
        insertDefault(new_fileSystem)

        filelist = FileSystem.objects.filter(member_id=id, filePath=filepath).order_by('fileName')
        context = {'filelist': filelist}

        return render(request, 'note/memo.html', context)


# task 변경
def changetask(request):
    id = request.session['user_id']
    filepath = request.GET['filepath']
    filelist = FileSystem.objects.filter(member_id=id, filePath=filepath).order_by('fileName')

    context = {'filelist': filelist}

    return render(request, 'note/memo.html', context)


# memo 변경
def changememo(request, task, memo):
    if not request.session._session:
        return render(request, 'note/404.html', status=404)
    id = request.session['user_id']
    if not FileSystem.objects.filter(member_id=id, filePath=task, fileName=memo):
        return render(request, 'note/404.html', status=404)
    pathlist = FileSystem.objects.filter(member_id=id).values('filePath').distinct().order_by('filePath')
    filelist = FileSystem.objects.filter(member_id=id, filePath=task).order_by('fileName')

    request.session['filepath'] = task
    request.session['filename'] = memo

    data = requestDB(id, task, memo)

    context = {
        'filelist': filelist,
        'pathlist': pathlist,
        'leftdata': data['leftdata'],
        'rightdata': data['rightdata']
    }

    return render(request, 'note/index.html', context)


# task 이름 수정
def renametask(request):
    id = request.session['user_id']
    old_name = request.POST['old']
    new_name = request.POST['new']

    if new_name.find("/") != -1:
        data = "unavailable"
        return HttpResponse(data)

    elif FileSystem.objects.filter(member_id=id, filePath=new_name).exists():
        data = "duplicated"
        return HttpResponse(data)

    else:
        if request.session['filepath'] == old_name:
            request.session['filepath'] = new_name

        filelist = FileSystem.objects.filter(member_id=id, filePath=old_name)
        for file in filelist:
            file.filePath = new_name
            file.save()

        contentlist = FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=old_name + "/"))
        for content in contentlist:
            str = content.fileName
            content.fileName = str.replace(old_name + "/", new_name + "/", 1)
            content.save()

        pathlist = FileSystem.objects.filter(member_id=id).values('filePath').distinct().order_by('filePath')
        context = {'pathlist': pathlist}
        return render(request, 'note/task.html', context)


# memo 이름 수정
def renamememo(request):
    id = request.session['user_id']
    filepath = request.POST['filepath']
    old_name = request.POST['old']
    new_name = request.POST['new']

    if new_name.find("/") != -1:
        data = "unavailable"
        return HttpResponse(data)

    elif FileSystem.objects.filter(member_id=id, filePath=filepath, fileName=new_name).exists():
        data = "duplicated"
        return HttpResponse(data)

    else:
        if request.session['filename'] == old_name:
            request.session['filename'] = new_name

        file = FileSystem.objects.get(member_id=id, filePath=filepath, fileName=old_name)
        file.fileName = new_name
        file.save()

        contentlist = FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=filepath + "/" + old_name + "/"))
        for content in contentlist:
            str = content.fileName
            content.fileName = str.replace(filepath + "/" + old_name + "/", filepath + "/" + new_name + "/", 1)
            content.save()

        filelist = FileSystem.objects.filter(member_id=id, filePath=filepath).order_by('fileName')
        context = {'filelist': filelist}
        return render(request, 'note/memo.html', context)


# task 삭제
def deletetask(request):
    id = request.session['user_id']
    selectedTask = request.POST['filepath']

    filelist = FileSystem.objects.filter(member_id=id, filePath=selectedTask)
    filelist.delete()
    FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=selectedTask + "/")).delete()

    pathlist = FileSystem.objects.filter(member_id=id).values('filePath').distinct().order_by('filePath')
    context = {'pathlist': pathlist}
    return render(request, 'note/task.html', context)


# memo 삭제
def deletememo(request):
    id = request.session['user_id']
    filepath = request.POST['filepath']
    selectedMemo = request.POST['filename']

    file = FileSystem.objects.get(member_id=id, filePath=filepath, fileName=selectedMemo)
    file.delete()
    FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=filepath + "/" + selectedMemo + "/")).delete()

    if not FileSystem.objects.filter(member_id=id, filePath=filepath):
        filepath = request.session['filepath']
        filelist = FileSystem.objects.filter(member_id=id, filePath=filepath).order_by('fileName')
    else:
        filelist = FileSystem.objects.filter(member_id=id, filePath=filepath).order_by('fileName')
    context = {'filelist': filelist}
    return render(request, 'note/memo.html', context)


# 해시태그 저장
def savehash(request):
    id = request.session['user_id']
    filepath = request.session['filepath']
    filename = request.session['filename']
    hash = request.POST['hash']

    if not HashList.objects.filter(member_id=id, filePath=filepath, fileName=filename, hash=hash).exists():
        HashList(member_id=id, filePath=filepath, fileName=filename, hash=hash).save()

    return HttpResponse()

# 해시태그 검색
def searchhash(request):
    id = request.session['user_id']
    hash = request.GET['hash']

    filelist = HashList.objects.filter(member_id=id, hash=hash).distinct().order_by('filePath')
    context = {'filelist': filelist}
    return render(request, 'note/hash.html', context)


def findId(request):
    if request.method == 'POST':

        name = request.POST.get('user_name')
        email = request.POST.get('user_mail')
        member_exist = Member.objects.filter(Q(name=name) & Q(email=email))

        if member_exist:
            member = Member.objects.get(name=name, email=email)
            sendmail = EmailMessage(
                '찾으시는 아이디입니다.',  # 제목
                member.member_id,  # 내용
                'rapidnotecapstone@gmail.com',  # 보내는 이메일 (settings에 설정해서 작성안해도 됨)
                to=[email],  # 받는 이메일 리스트
            )
            sendmail.send()
            messages.info(request, '가입하신 이메일로 아이디를 전송했습니다.')
            return redirect('note:login')
        else:
            messages.info(request, 'id가 존재하지 않습니다.')
            return redirect('note:findIdPw')


def findPw(request):
    if request.method == 'POST':
        id = request.POST.get('user_id')
        name = request.POST.get('user_name')
        email = request.POST.get('user_mail')
        member_exist = Member.objects.filter(Q(member_id=id) & Q(name=name) & Q(email=email))
        if member_exist:
            member = Member.objects.get(member_id=id, name=name, email=email)
            sendmail = EmailMessage(
                '찾으시는 비밀번호입니다.',  # 제목
                member.pw,  # 내용
                'rapidnotecapstone@gmail.com',  # 보내는 이메일 (settings에 설정해서 작성안해도 됨)
                to=[email],  # 받는 이메일 리스트
            )
            sendmail.send()
            messages.info(request, '가입하신 이메일로 비밀번호를 전송했습니다.')
            return redirect('note:login')
        else:
            messages.info(request, 'id가 존재하지 않습니다.')
            return redirect('note:findIdPw')


def error_page(request, *args, **argv):
    return render(request, 'note/404.html', status=404)


"""""""""""""""""""""""""""
▼▼  CODE FOR ANDROID  ▼▼
"""""""""""""""""""""""""""


@api_view(['POST'])
def app_login(request):
    if request.method == 'POST':
        # 안드로이드랑 포맷 맞춰야함
        print(request.POST)
        id = request.data.get('userId')
        password = request.data.get('password')
        member_exist = Member.objects.filter(Q(member_id=id) & Q(pw=password))
        if member_exist:
            success = {
                "userId": id,
                "displayName": id  #이름 받는 부분입니데이
            }
            print("login success at app login")
            return JsonResponse(success)
        else:
            fail = {
                "userId": "fail1",
                "displayName": "fail2"  # 이름 받는 부분입니데이
            }
            print("login failed at app login", id, password)
            return JsonResponse(fail)


@api_view(['POST'])
def app_insertDB(request):
    id = request.data.get('id')
    task_name = request.data.get('task_name')
    memo_name = request.data.get('memo_name')
    memo_content = request.data.get('memo_content')
    print(id, task_name, memo_name)
    if Member.objects.filter(Q(member_id=id)):
        if FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=task_name+"/"+memo_name+"/left")):
            FileList.objects.filter(Q(member_id=id) & Q(fileName__startswith=task_name + "/" + memo_name + "/left")).delete()
            for i in range(0, math.ceil(len(memo_content)/3500)):
                new_fileList = FileList(member_id=id, fileName=task_name + "/" + memo_name + "/left" + str(i),
                                        fileContent=memo_content[i * 3500:(i * 3500) + 3500])
                new_fileList.save()
        success = {"id": id,
                   "code": "success"}
        return JsonResponse(success)
    else:
        fail = {"id": id,
                "code": "fail"}
        return JsonResponse(fail)
