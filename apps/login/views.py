from django.shortcuts import render,HttpResponse
from django.shortcuts import redirect

from django.conf import settings
from . import models
from apps.confer_manage import models as cm_models
from . import forms

import hashlib
from django.views.decorators.csrf import csrf_exempt

import datetime
import re

import logging

# logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('django')

# Create your views here.



def hash_code(s, salt='piston'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自会议管理系统的测试邮件'

    text_content = '欢迎访问zhce的会议管理系统，这里是数鼎科技分析与建模分队的会议管理站点，欢迎加入，一起愉快的开会！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.piston_meeting.com</a>，\
                    这里是数鼎科技分析与建模分队的会议管理站点，欢迎加入，一起愉快的开会！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('192.168.1.209:8080', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def index(request):   #貌似没有用处
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return redirect('confer_manage:dashboard')


def blog(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return redirect('sharing:index')


def appplat(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    try:
        user_id = request.session.get('user_id')
        user = models.User.objects.get(id=user_id)
        pic = user.picture.url
    except:
        user={'picture':{'url':'adminlet-2.4.10/dist/img/avatar.png'}}
        pic = '/media/image/avatar.png'

    request.session['avatar'] = pic
    print(pic)
    return render(request, 'plat.html', locals())

@csrf_exempt
def login(request):
    if request.session.get('is_login', None):  # 不允许重复登录
        return redirect('/appplat/')
    if request.method == 'POST':
        logger.info(['login:', 'POST'])
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            logger.info([username, 'login:', 'input valid'])

            try:
                phone_pattern=re.compile('\d{11}')
                if re.fullmatch(phone_pattern,username):
                    user = models.User.objects.get(phone=username)
                else:
                    user = models.User.objects.get(name=username)
            except:
                message = '用户不存在！'
                logger.info([username,'login:', message])
                return render(request, 'login/login.html', locals())

            if not user.has_confirmed:
                message = '该用户还未经过邮件确认！'
                logger.info([username, 'login:', message])
                return render(request, 'login/login.html', locals())

            if user.password == hash_code(password) or user.password == password:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                logger.info([username, 'login:', '登录成功'])
                return redirect('/appplat/')
            else:
                message = '密码不正确！'
                return render(request, 'login/login.html', locals())
        else:
            logger.info(['login:', 'input invalid'])
            logger.info(['login:', login_form.errors])
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    logger.info(['login:', 'GET'])
    return render(request, 'login/login.html', locals())

@csrf_exempt
def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            phone = register_form.cleaned_data.get('phone')
            sex = register_form.cleaned_data.get('sex')
            role = register_form.cleaned_data.get('role')
            apartment=register_form.cleaned_data.get('apartment')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'login/register.html', locals())
                same_phone_user = models.User.objects.filter(phone=phone)
                if same_phone_user:
                    message = '该手机已经被注册了！'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()

                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.phone = phone
                new_user.sex = sex
                new_user.role = role
                new_user.apartment=cm_models.Apartment.objects.get(id=apartment)
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '请前往邮箱进行确认'
                return render(request, 'login/confirm.html', locals())
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())

import json
# 验证码需要导入的模块
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
def refresh_captcha(request):
    print(1000)
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    captcha = {'hashkey': hashkey, 'image_url': image_url}
    return HttpResponse(json.dumps(captcha), content_type='application/json')

#以下修改密码
def send_email4psw(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '【Piston Support System】重置密码'

    text_content = '请点击以下链接进行重置您的密码：http://{}/psw_reset/?code={}'.format('127.0.0.1:8000', code, 1)

    html_content = '''
                    <p>请点击以下链接进行重置您的密码：<a href="http://{}/psw_reset/?code={}" target=blank>www.pssresetpwd.com</a></p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('192.168.1.209:8080', code, 1)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@csrf_exempt
def forgotpsw(request):
    if request.method == 'POST':
        user_forget_form = forms.UserForgetForm(request.POST)
        if user_forget_form.is_valid():
            email = user_forget_form.cleaned_data['email']
            user = models.User.objects.get(email=email)
            if user:
                send_email4psw(email, user.id)
                return HttpResponse('请尽快去您的邮箱重置密码')
            else:
                return render(request, 'login/forgotpsw.html', {
                    'msg': '用户不存在',
                    'user_forget_form': user_forget_form
                })
        else:
            return render(request, 'login/forgotpsw.html', {
                'user_forget_form': user_forget_form
            })
    user_forget_form = forms.UserForgetForm()
    return render(request, 'login/forgotpsw.html', locals())

@csrf_exempt
def psw_reset(request):
    print(10000)
    if request.method=='GET':
        code = request.GET.get('code', None)
        message = ''
        try:
            print(code)
            user = models.User.objects.get(id=code)
            print(user)
            username=user.name
            email=user.email
            data={'email':email}
            resetpswform=forms.ResetPswForm(data=data)
            return render(request, 'login/resetpsw.html', locals())
        except:
            message = '无效的确认请求!'
            return render(request, 'login/forgotpsw.html', locals())
    elif request.method=='POST':
        resetpswform=forms.ResetPswForm(request.POST)
        ret = {"status": None, "message": None}
        if resetpswform.is_valid():
            print(22222)
            email=resetpswform.cleaned_data.get('email')
            user = models.User.objects.get(email=email)
            password1 = resetpswform.cleaned_data.get('password1')
            password2 = resetpswform.cleaned_data.get('password2')
            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/resetpsw.html', locals())
            else:
                user.password=hash_code(password1)
                user.save()
                ret['status']='成功'
                return HttpResponse('密码修改成功，请前往登录页面重新登录')
        else:
            print(5555)
            print(resetpswform.errors)
            return render(request, 'login/resetpsw.html', locals())



