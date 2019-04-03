from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.auth.models import User
from core.Backends.db_method import save_weibo_db,fetch_weibo_by_user_name
from web.models import Weibo, UserProfile
# Create your views here.
from core.custom_queue import msgQueue
from Weibo import settings
from core.Backends import db_method
from core import redis_helper
import json
import time
from django.core.mail import send_mail
from django.conf import settings
from web import models
from django.core import serializers
from web.models import Weibo, UserProfile,Comment

gloabal_imgfile=""
# 用于检查用户是否登录
# @login_required
#
topic=None
nextpage=None
range_page=0
def index(request):
    # 访问首页
    print("进入index")
    uid = request.session['uid']
    global topic
    global nextpage
    if request.GET.get('topicc')!=None:
        topic = request.GET.get('topicc')
    nextpage = request.GET.get('nextpage')
    print("topic" + str(topic))
    print("nextpage" + str(nextpage))
    print(uid)
    print("退出index")
    user = User.objects.get(id=uid)########################
    #print(user)
    username = user.username
    userprofile=UserProfile.objects.get(user=user)


    return render(request, 'Home/index.html', {'userprofile':userprofile,'user_id': uid, 'username': username})########################

def visit(request):
    # 访问首页
    uid = request.session['uid']
    user = User.objects.get(id=uid)  ########################
    # print(user)
    username = user.username
    print(uid)

    return render(request, 'Home/visit.html', {'user_id': uid, 'username': username})#
# @csrf_protect
@csrf_exempt
def create_wb(request):
    """创建、发布微博"""
    print("进入发布微博")
    ret = {'status': True, 'data': ''}
    try:
        # 获取发过来的微博消息详细
        # {'data': {'viedo': '', 'content': '[em_28]hello python', 'time': 1474954943.9340596, 'wb_type': 0, 'topic': '', 'uid': ''}, 'status': True}
        data_str = request.POST.get('data', None)

        print(data_str)

        data_dict = json.loads(data_str)
        wb_type = data_dict['wb_type'] # 类型
        #print("wb_type"+str(wb_type))
        user = data_dict['uid']  # 用户id
        #print("uid"+str(user))
        perat=[]
        text = data_dict['content']  # wei文博正文

        #print("content"+str(text))
        user_obj = models.UserProfile.objects.get(id=user)  # user_obj

        print(text)
        strtext = str(text)
        if strtext.find("@"):
            print("perat空")
        else:
            print("进入else")
            perat = strtext.split("@")
            perat.pop(0)
            dataat = []
            print(perat)
            for p in perat:
                print(p)
                blank = []
                if p.find(" ") == -1:
                    print("不存在空格")
                else:
                    blank = p.split(" ")
                    dataat.append(blank[0])  # 插入第一个at的人
                    be_at = models.UserProfile.objects.get(name=blank[0])
                    old_at_message = be_at.at_message
                    be_at.at_message = old_at_message +user_obj.name+" 在他/她的微博："+strtext+" 中提到了你"+"\n"
                    be_at.save()
                    #print("flag////")
                    #print(be_at.name)
                    #print(be_at.at_message)

            print(dataat)
        new = models.Weibo()
        #print("打印global"+str(gloabal_imgfile))
        global gloabal_imgfile
        new.pictures_link_id=gloabal_imgfile
        print("gloabal_imgfile: "+str(gloabal_imgfile));
        gloabal_imgfile=""
        new.user = user_obj
        new.name=user_obj.name
        new.perm = data_dict['perm']
        print("create里面打印perm："+str(new.perm))
        print(new.name)
        new.wb_type = wb_type
        new.text = text
        new.date='2018-01-01'
        new.user_id=data_dict['uid']
        new.save()
        print(new);
        print("save jieshu")
        # 微博发布时间
        data_dict['time'] = time.time()

        # 消息队列实例
        msg_queue = msgQueue()
        # 连接rabbitmq服务器
        msg_queue.make_conn()
        # 执行消息队列发布方法
        msg_queue.publish_wb(data_dict)

        ret['data'] = data_dict

        #print(ret)
        weibos=models.User.objects.get(id=1)
    except Exception as e:
        ret['status'] = False
        print('error', e)
    wbo_text = models.Weibo.objects.all()
    wbo_text_1=models.Weibo.objects.filter(id=5)
    #return render(request,'Home/index.html',locals())
    return HttpResponse(json.dumps(ret), locals())

def create_cm(request):
    """创建、发布微博"""
    print("进入发布评论");
    data_str = request.POST.get('data', None)

    print(data_str)

    data_dict = json.loads(data_str)
    #ret = {'status': True, 'data': ''}
    #return HttpResponse(json.dumps(ret))
    print("create_get_comment")
    wb_id=data_dict['wb_id']
    wb_publisher=models.Weibo.objects.get(id=wb_id).user
    print("ok1")
    to_crspd_weibo=models.Weibo.objects.get(id=wb_id)
    print("ok2")
    cm_publisher=models.UserProfile.objects.get(id=data_dict['uid'])
    print("ok3")
    atn=wb_publisher.attention
    if wb_publisher.id!=cm_publisher.id:
        atn = atn + str(cm_publisher.name) + " 评论了你的微博：" + "#" + str(to_crspd_weibo.text) + "#" + "</br>"
    print(atn)
    wb_publisher.attention=atn
    wb_publisher.save()
    print("ok1")
    new_cm=models.Comment()
    print("ok2")
    new_cm.user_id=data_dict['uid']
    print("ok3")
    new_cm.to_weibo_id=wb_id
    print("ok4")
    new_cm.comment=data_dict['content']
    new_cm.date='2018-01-01'
    new_cm.p_comment=1
    cm_to_user=models.UserProfile.objects.get(id=data_dict['uid'])
    cm_to_weibo=models.Weibo.objects.get(id=wb_id)
    count=cm_to_weibo.hot
    count=count+1
    cm_to_weibo.hot=count
    cm_to_weibo.save()
    new_cm.name=cm_to_user.name
    new_cm.save()
    # 获取此用户队列内的新消息
    wb_comment = models.Comment.objects.filter(to_weibo_id=wb_id)#找到tid号微博对应的所有的评论
    print("打印更新后的所有微博评论")
    print(wb_comment)
    #old_wb_query = list(old_wb_query)
    wb_comment = serializers.serialize("json", wb_comment)
    print(wb_comment)
    #return JsonResponse(old_wb_query,safe=False)
    #return old_wb_query
    #return JsonResponse(old_wb_query,safe=False)
    return HttpResponse(wb_comment,content_type="application/json")
    #return

def get_new_wb_count(request):
    # 用户获取各自消息队列中新微博数量
    user_id = request.GET.get('user_id')
    msg_queue = msgQueue()
    msg_queue.make_conn()
    # 获取此用户队列类的新消息数
    count = msg_queue.get_new_wb_count("uid_%s" % (user_id,))
    return HttpResponse(json.dumps({'new_wb_count': count}))


def get_new_wb(request):
    # 用户获取各自队列中新的微博消息列表
    print("get_old_wb")
    user_id = request.GET.get('user_id')
    # 获取此用户队列内的新消息
    old_wb_query = models.Weibo.objects.all()
    tiaoshu=old_wb_query.count()
    print(old_wb_query)
    #old_wb_query = list(old_wb_query)
    old_wb_query = serializers.serialize("json", old_wb_query)
    print(old_wb_query)
    #return JsonResponse(old_wb_query,safe=False)
    #return old_wb_query
    #return JsonResponse(old_wb_query,safe=False)
    return HttpResponse(old_wb_query,content_type="application/json")

def get_old_wb(request):
    # 用户获取各自队列中新的微博消息列表
    page_size=4
    #print("get_old_wb")
    user_id = request.GET.get('user_id')
    #print("topoc")
    global topic
    global nextpage
    global range_page
    #print(topic)
    #print(nextpage)
    if nextpage==None:
        range_page=0
    # 获取此用户队列内的新消息
    if topic==None:
        #print("全部")
        if nextpage=='2':
         #   print("下一页")
            if models.Weibo.objects.all().count()-range_page>page_size:
                range_page = range_page + page_size
            old_wb_query = models.Weibo.objects.all().order_by('-id')[range_page:range_page+page_size]
        elif nextpage=='1':
          #  print("全页")
            if range_page!=0:
                range_page = range_page - page_size
            old_wb_query = models.Weibo.objects.all().order_by('-id')[range_page:range_page+page_size]
        else:
            old_wb_query = models.Weibo.objects.all().order_by('-id')[range_page:range_page+page_size]
    elif topic=='6':
        #print("全部")
        if nextpage=='2':
         #   print("下一页")
            if models.Weibo.objects.all().count()-range_page>page_size:
                range_page = range_page + page_size
            old_wb_query = models.Weibo.objects.all().order_by('-id')[range_page:range_page+page_size]
        elif nextpage=='1':
          #  print("全页")
            if range_page!=0:
                range_page = range_page - page_size
            old_wb_query = models.Weibo.objects.all().order_by('-id')[range_page:range_page+page_size]
        else:
            old_wb_query = models.Weibo.objects.all().order_by('-id')[range_page:range_page+page_size]
    elif topic=='0':#热点
        #print("全部0")
        if nextpage=='2':
         #   print("下一页")
            if models.Weibo.objects.all().count()-range_page>page_size:
                range_page = range_page + page_size
            old_wb_query = models.Weibo.objects.all().order_by('-hot')[range_page:range_page+page_size]
        elif nextpage=='1':
          #  print("全页")
            if range_page!=0:
                range_page = range_page - page_size
            old_wb_query = models.Weibo.objects.all().order_by('-hot')[range_page:range_page+page_size]
        else:
            old_wb_query = models.Weibo.objects.all().order_by('-hot')[range_page:range_page+page_size]
    else:#话题
        #print("部分")
        if nextpage=='2':
         #   print("下一页")
            if models.Weibo.objects.all().count()-range_page>page_size:
                range_page = range_page + page_size
            old_wb_query = models.Weibo.objects.filter(perm=topic).order_by('-id')[range_page:range_page+page_size]
        elif nextpage=='1':
          #  print("全页")
            if range_page!=0:
                range_page = range_page - page_size
            old_wb_query = models.Weibo.objects.filter(perm=topic).order_by('-id')[range_page:range_page+page_size]
        else:
            old_wb_query = models.Weibo.objects.filter(perm=topic).order_by('-id')[range_page:range_page+page_size]
    nextpage = None
    #old_wb_query = models.Weibo.objects.all().order_by('-hot')
    tiaoshu=old_wb_query.count()
    #print(old_wb_query)
    #old_wb_query = list(old_wb_query)
    old_wb_query = serializers.serialize("json", old_wb_query)
    #print(old_wb_query)
    #return JsonResponse(old_wb_query,safe=False)
    #return old_wb_query
    #return JsonResponse(old_wb_query,safe=False)
    return HttpResponse(old_wb_query,content_type="application/json")

def create_cm_follow(request):
    """创建、发布微博"""
    print("进入评论回复");
    data_str = request.POST.get('data', None)

    print(data_str)

    data_dict = json.loads(data_str)
    #ret = {'status': True, 'data': ''}
    #return HttpResponse(json.dumps(ret))
    print("create_comment_follow")
    cm_id=data_dict['cm_id']#获取评论对应的id
    parent_cm=models.Comment.objects.get(id=cm_id)#父评论
    cm_publisher=parent_cm.user
    anser=models.UserProfile.objects.get(id=data_dict['uid'])#回复者
    atn=cm_publisher.attention
    if anser.id!=cm_publisher.id:
        atn = atn + str(anser.name) + " 回复了你的评论：" + "#" + str(parent_cm.comment) + "#" + "\n"+"</br>"
    print(atn)
    cm_publisher.attention=atn
    cm_publisher.save()
    count=parent_cm.hot
    count=count+1
    parent_cm.hot=count
    parent_cm.save()#父评论的回复数+1
    print("ok1")
    new_cm=models.Comment()
    print("ok2")
    new_cm.user_id=data_dict['uid']
    print("ok3")
    new_cm.to_weibo_id=parent_cm.to_weibo_id
    print("ok4")
    new_cm.comment=data_dict['content']
    new_cm.parent_name=parent_cm.name
    new_cm.date='2018-01-01'
    new_cm.p_comment=parent_cm.hot
    cm_to_user=models.UserProfile.objects.get(id=data_dict['uid'])
    cm_to_weibo=models.Weibo.objects.get(id=parent_cm.to_weibo_id)
    count=cm_to_weibo.hot
    count=count+1
    cm_to_weibo.hot=count
    cm_to_weibo.save()
    new_cm.name=cm_to_user.name
    new_cm.save()
    # 获取此用户队列内的新消息
    wb_comment = models.Comment.objects.filter(to_weibo_id=parent_cm.to_weibo_id).order_by('-to_weibo_id','p_comment')#找到tid号微博对应的所有的评论
    print("打印更新后的所有微博评论")
    print(wb_comment)
    #old_wb_query = list(old_wb_query)
    wb_comment = serializers.serialize("json", wb_comment)
    print(wb_comment)
    #return JsonResponse(old_wb_query,safe=False)
    #return old_wb_query
    #return JsonResponse(old_wb_query,safe=False)
    return HttpResponse(wb_comment,content_type="application/json")
    #return

def upload_file(request):
    print("提交图片")
    # 用户上传图片
    if request.method == 'POST':
        print(request.FILES)
        file_obj = request.FILES.get('file', None)
        global gloabal_imgfile
        gloabal_imgfile=file_obj
        #print(gloabal_imgfile)
        recv_size = 0
        # 服务端保存
        cache.delete(file_obj.name)
        # uid = request.user.userprofile.id
        uid = 1
        file_path = "%s/%s/temp/%s" %(settings.FILE_PATH,uid,file_obj.name)
        with open(file_path, 'wb+') as temp:
            for chunk in file_obj.chunks():
                temp.write(chunk)
                recv_size += len(chunk)
                cache.set(file_obj.name, recv_size)

        return HttpResponse(json.dumps({'status': True, 'filename': file_obj.name}))

def message(request):
    user_id=request.session['uid']
    print("进入message"+str(user_id))
    msg=models.UserProfile.objects.get(id=user_id).attention
    upf=models.UserProfile.objects.get(id=user_id)
    upf.attention=""
    upf.save()
    return render(request, 'Home/message.html', {'msg': msg})

def at_message(request):
    user_id=request.session['uid']
    print("进入at_message"+str(user_id))
    msg=models.UserProfile.objects.get(id=user_id).at_message
    print(msg)
    upf=models.UserProfile.objects.get(id=user_id)
    upf.at_message=""
    upf.save()
    return render(request, 'Home/at_message.html', {'msg': msg})

def get_comment(request):
    # 用户获取各自队列中新的微博消息列表
    print("get_comment")
    wb_id = request.GET.get('tid')
    # 获取此用户队列内的新消息
    wb_comment = models.Comment.objects.filter(to_weibo_id=wb_id).order_by('-to_weibo_id','p_comment')#找到tid号微博对应的所有的评论
    tiaoshu=wb_comment.count()
    print(wb_comment)
    #old_wb_query = list(old_wb_query)
    wb_comment = serializers.serialize("json", wb_comment)
    print(wb_comment)
    #return JsonResponse(old_wb_query,safe=False)
    #return old_wb_query
    #return JsonResponse(old_wb_query,safe=False)
    return HttpResponse(wb_comment,content_type="application/json")
    #return


def upload_file_progress(request):
    # 获取文件上传进度
    if request.method == 'GET':
        filename = request.GET.get('filename')
        upload_progress = cache.get(filename)
        return HttpResponse(json.dumps({'received_size': upload_progress}))
    else:
        cache_key = request.POST.get('cache_key')
        cache.delete(cache_key)
        return HttpResponse("cache key[%s] got deleted" % cache_key)


@login_required
def home(request):
    # 个人主页
    if request.method == 'GET':
        uid = request.GET.get('uid')
        user = User.objects.get(id=uid)
        username = user.username
        userprofile=UserProfile.objects.get(user=user)
        userbrief = userprofile.brief
        weibos = fetch_weibo_by_user_name(username)
        my_followers = userprofile.follow_list
        print(my_followers)
        return render(request, 'Home/home.html',{'userprofile':userprofile,'user_id': uid, 'username': username,'weibos': weibos,'userbrief': userbrief})
    else:
        uid = request.GET.get('uid')
        user = UserProfile.objects.filter(id=uid)
        username = user.username
        weibos = fetch_weibo_by_user_name(username)
        return render(request, 'Home/home.html',{'user_id': uid,  'username': username,'weibos': weibos})


def otherhome(request):
    # 个人主页
    if request.method == 'GET':
        uid = request.GET.get('uid')
        user = User.objects.get(id=uid)
        curid=request.GET.get('curid')
        curuser=UserProfile.objects.get(id=curid)
        username = user.username
        userprofile=UserProfile.objects.get(user=user)
        userbrief = userprofile.brief
        weibos = fetch_weibo_by_user_name(username)
        my_followers = userprofile.follow_list
        follow_list=userprofile.follow_list
        following=my_followers.filter()
        print(my_followers)
        if uid==curid:

            return render(request, 'Home/home.html',
                          {'curuser': curuser, 'following': following, 'follow_list': follow_list,
                           'my_followers': my_followers, 'userprofile': userprofile, 'user_id': uid,
                           'username': username, 'weibos': weibos, 'userbrief': userbrief})

        else:
            return render(request, 'Home/otherhome.html',{'curuser':curuser,'following':following,'follow_list':follow_list,'my_followers':my_followers,'userprofile':userprofile,'user_id': uid, 'username': username,'weibos': weibos,'userbrief': userbrief})
    else:
        uid = request.POST.get('uid')
        #curid = request.GET.get('curid')
        curname = request.POST.get('curname')
        curuser= UserProfile.objects.get(name=curname)
        curid=curuser.user_id
        #my_followers=request.POST.get('my_followers')
        #follow_list = request.POST.get('follow_list')
        user = User.objects.get(id=uid)
        userprofile = UserProfile.objects.get(user=user)
        userbrief=userprofile.brief
        userweibo = Weibo.objects.filter(user=userprofile)
        userweibonum = userweibo.count
        username = user.username
        my_followers = userprofile.my_followers
        follow_list = userprofile.follow_list
        curuserweibo = Weibo.objects.filter(user=curuser)
        curuserweibonum = curuserweibo.count
        #curname=curuser.name
        curweibos=fetch_weibo_by_user_name(curname)
        print(my_followers.count())
        f= request.POST.get('f')
        print("这是f")
        print(f)
        weibos = fetch_weibo_by_user_name(username)
        if (my_followers.count())!= 0:#有人关注
            #following = my_followers.filter(id=curid)

            following=my_followers.filter(id=curid)
            print(following)

            if (following.count()) == 1:#当前用户关注了
                if f == '0':#-》取关
                    userprofile.my_followers.remove(curuser)#当前页面用户的一个粉丝被移出
                    curuser.follow_list.remove(userprofile)#登录用户的一个关注被移除
                    my_followers = userprofile.my_followers
                    follow_list = userprofile.follow_list
                    print(my_followers.count())
                    #return render(request,'Home/follow.html')
                    #return render(request, 'Home/home.html',
                              #{'f':f,'user_id': curid, 'username': curname, 'weibos': curweibos, 'userweibonum': curuserweibonum})
                #elif f=='1':#不取关
                return render(request, 'Home/otherhome.html',
                              {'f': f, 'user_id': uid, 'username': username,
                               'weibos': weibos,'userweibonum': userweibonum,
                               'curname': curname, 'curuser': curuser,
                               'userprofile': userprofile, 'userbrief': userbrief,
                               'follow_list': follow_list, 'my_followers': my_followers,
                               })

            elif (following.count()) == 0:#当前用户没有关注
                if f == '1':#-》关注
                    userprofile.my_followers.add(curuser)# 为当前页面用户添加一个粉丝
                    curuser.follow_list.add(userprofile)  # 登录用户增加一个关注
                    my_followers = userprofile.my_followers
                    follow_list = userprofile.follow_list

                print(my_followers.count())
                #return render(request, 'Home/notfollow.html')
                return render(request, 'Home/otherhome.html',{
                    'f':f,'user_id': uid,
                    'username': username,'weibos': weibos,
                    'userweibonum':userweibonum,'curname': curname,
                    'curuser': curuser,
                    'userprofile': userprofile, 'userbrief': userbrief,
                    'follow_list': follow_list, 'my_followers': my_followers,
                })

        else:#无人关注-》当前用户没有关注-》关注
            if f == '1':
                userprofile.my_followers.add(curuser)  # 为当前页面用户添加一个粉丝
                curuser.follow_list.add(userprofile)  # 登录用户增加一个关注
                my_followers = userprofile.my_followers
                follow_list = userprofile.follow_list

            print(my_followers.count())
            return render(request, 'Home/otherhome.html',{
                'f':f,'user_id': uid,  'username': username,
                'weibos': weibos,'userweibonum':userweibonum,
                'curname': curname, 'curuser': curuser,
                'userprofile': userprofile, 'userbrief': userbrief,
                'follow_list': follow_list, 'my_followers': my_followers,
            })


def search(request):
    # 搜索
    if request.method == 'GET':
        text = request.GET.get('text')
        curid=request.GET.get('user_id')
        curname = request.POST.get('username')
        curuser = UserProfile.objects.get(name=curname)
        curid=curuser.user_id
        return render(request, 'Search/search.html',{
            'curuser':curuser,'curid':curid,
            'text':text,'curid':curid})

    elif request.method == 'POST':
        text = request.POST['text']
        print(text)
        curname = request.POST.get('username')
        print(curname)
        curuser = UserProfile.objects.get(name=curname)
        finduser = UserProfile.objects.filter(name__contains=text)
        userweibo=Weibo.objects.filter(user=finduser)
        userweibonum=userweibo.count
        curid = curuser.user_id
        #curuser=UserProfile.objects.filter(id=curid)
        findweibo = Weibo.objects.filter(text__contains=text)
        return render(request, 'Search/search.html',{
            'username':curname,'curname':curname,
            'curuser':curuser,'curid':curid,
            'text':text,'finduser':finduser,
            'findweibo':findweibo,'userweibonum':userweibonum,})


def search2(request):
    # 搜索
    if request.method == 'GET':
        text = request.GET.get('text')
        curid=request.GET.get('user_id')
        curname = request.POST.get('username')

        curuser = UserProfile.objects.get(name=curname)

        curid=curuser.user_id
        return render(request, 'Search/search.html',{'curuser':curuser,'curid':curid,'text':text,'curid':curid})
    elif request.method == 'POST':
        text = request.POST['text']
        uid=request.POST['uid']
        user = User.objects.get(id=uid)
        username = user.username
        userprofile = UserProfile.objects.get(user=user)
        userbrief = userprofile.brief
        weibos = fetch_weibo_by_user_name(username)
        my_followers = userprofile.my_followers
        follow_list = userprofile.follow_list
        #following = my_followers.filter()
        print(my_followers)
        print("这是关注列表！！！")
        print(follow_list)
        print(follow_list.count())
        print("这是关注列表！！！")
        print(uid)
        print(text)
        curname = request.POST.get('username')
        print(curname)
        curuser = UserProfile.objects.get(name=curname)
        finduser = UserProfile.objects.filter(name__contains=text)
        userweibo=Weibo.objects.filter(user=finduser)
        userweibonum=userweibo.count
        curid = request.POST['curid']
        print(curid)
        #curuser=UserProfile.objects.filter(id=curid)
        findweibo = Weibo.objects.filter(text__contains=text)
        if uid == curid:
            return render(request, 'Home/home.html',
                          {'username': curname, 'curname': curname,'weibos': weibos,
                           'curuser': curuser, 'user_id': curid,'username': username,
                           'text': text,'finduser': finduser,'userprofile': userprofile,
                           'userbrief': userbrief, 'follow_list': follow_list,
                           'findweibo': findweibo, 'userweibonum': userweibonum,
                           'my_followers': my_followers,
                           })
        else:

            following=my_followers.filter(id=curid)
            print(following)

            if (following.count()) == 1:#已关注
                f = 1

            else:#未关注
                f=0
            print(f)
            return render(request, 'Home/otherhome.html', {
                'user_id': uid, 'username': username,
                'curname': curname, 'curuser': curuser,
                'text': text, 'f': f,
                'userprofile': userprofile, 'userbrief': userbrief,
                'finduser': finduser, 'findweibo': findweibo,
                'userweibonum': userweibonum, 'weibos': weibos,
                'follow_list': follow_list, 'my_followers': my_followers, })




def login_view(request):
    if request.method == "POST":
        post_data = request.POST.get('post_data', None)
        respons_status = {}

        if post_data:
            post_dic = json.loads(post_data)
            flag = post_dic['flag']
            if flag == '0':  # 使用Django自带验证功能做验证
                user_name = post_dic['user']
                passwd = post_dic['passwd']
            else:
                user_name = '1'
                passwd = '1'
            user2 = authenticate(username=user_name, password=passwd)
            if (UserProfile.objects.filter(name=user_name)):
                user1 = UserProfile.objects.get(name=user_name)
                if passwd == user1.password:
                    user = User.objects.get(username=user_name)
                    if user is not None:
                        # the password verified for the user
                        if user.is_active:
                            # print("User is valid, active and authenticated")
                            # 存入uid,name到session
                            data = db_method.fetch_user_info_by_name(user_name)
                            request.session['uid'] = data['uid']
                            request.session['name'] = data['name']

                            # 放入活跃用户列表
                            re_helper = redis_helper.redis_helper()
                            re_helper.r.set(data['uid'], "RECENT_USER", ex=86400)
                            # print('[x] 活跃用户', re_helper.r.get(data['uid']))

                            login(request, user)
                            respons_status['status'] = True
                            respons_status = json.dumps(respons_status)

                            # print("[auth]", request.user.is_authenticated)
                            return HttpResponse(respons_status)
                        else:
                            # print("The password is valid, but the account has been disabled!")
                            pass
                else:
                    # the authentication system was unable to verify the username and password
                    # print("The username and password were incorrect.")
                    respons_status['status'] = False
                    respons_status['message'] = "The username and password were incorrect."
                    respons_status = json.dumps(respons_status)
                    return HttpResponse(respons_status)
            else :
                respons_status['status'] = False
                respons_status['message'] = "The user could not be found."
                respons_status = json.dumps(respons_status)
                return HttpResponse(respons_status)
        else:
            respons_status['status'] = False
            respons_status['message'] = "Invalid username and password."
            respons_status = json.dumps(respons_status)
            return HttpResponse(respons_status)

    else:
        # 有登录就给跳到index, 否则显示login页面
        return render(request, 'Login/login.html')


def logout_view(request):
    print("退出123")
    if request.method == "GET":
        # 登出session
        request.session['uid']=""
        logout(request)
        return redirect('/login/')

def register(request):
    if(request.method=='GET'):
        return render(request, 'Login/register.html')
    elif(request.method=='POST'):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        brief = request.POST.get('brief')
        sex = request.POST.get('sex')
        age = request.POST.get('age')
        if (UserProfile.objects.filter(name=name)):
            return render(request, 'Login/register.html', {'note':"该用户名已注册"})
        elif password1 != password2:
            return render(request, 'Login/register.html', {'note': "密码不一致"})
        else:

            User.objects.create_user(username=name, password=password1, email=email)
            user1 = User.objects.get(username=name)
            user = UserProfile(name=name, password=password1, email=email,user_id=user1.id,brief=brief,sex=sex,age=age)
            user.save()
            user1.save()
            return render(request, 'Login/login.html')

def send(request):
    if request.method == 'GET':
        return render(request, 'Login/forget.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        if (UserProfile.objects.filter(email = email)):
                import string, random
                capta = ''
                words = ''.join((string.ascii_letters, string.digits))
                for i in range(6):
                    capta += random.choice(words)
                #tulps = eval(email)
                #print(tulps)
                msg = '你请求重置密码，验证码为'+capta
                send_mail('测试邮件01', msg, settings.EMAIL_FROM, [email])
                note = "发送成功"
                return render(request, 'Login/reset.html',{'note': note, 'capta': capta})
        else:
            note = "找不到该用户"
            return render(request,'Login/forget.html',{'note': note})

def reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        capta1 = request.POST.get('capta')
        capta2 = request.POST.get('capta2')
        if capta1 == capta2:
            if password1 == password2:
                user = UserProfile.objects.get(email=email)
                user.password = password1
                user1 = User.objects.get(email=email)
                user1.set_password(password1)
                user1.save()
                user.save()
                note = "密码修改成功"
            return render(request, 'Login/reset.html', {'note': note})
        else:
            note = "验证码错误"
            return render(request, 'Login/reset.html',{'capta': capta1, 'note': note})
    if request.method == 'GET':
        return render(request, 'Login/reset.html')

def dellist(request):
    if request.method == 'GET':
        webid = request.GET['webid']  # 获取删除条目的编号
        weibo = Weibo.objects.get(id=webid)
        userprofile = UserProfile.objects.get(user_id=weibo.user_id)
        uid=weibo.user_id
        Comment.objects.filter(to_weibo_id=webid).delete()
        Weibo.objects.get(id=webid).delete()

        username=userprofile.name
        userbrief=userprofile.brief
        weibos=Weibo.objects.filter(user_id=uid).order_by('-date')
        #person = Person.objects.filter(user=user).order_by(date)
        return render(request, 'Home/home.html', {'weibos':weibos,'userprofile': userprofile, 'uid':uid,'username':username,'userbrief':userbrief,})