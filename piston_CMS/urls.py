"""piston_CMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
import xadmin
from django.urls import path,re_path
from apps.login import views
from apps.confer_manage import views as c_views
from django.urls import include

from django.views import static ##新增
from django.conf import settings ##新增
from django.conf.urls import url ##新增
import notifications.urls

urlpatterns = [
    path('', views.login),
    path('admin/', xadmin.site.urls),
	path('mdeditor/', include('mdeditor.urls')),
    path('index/', views.index),
	path('appplat/', views.appplat),
	path('blog/', views.blog),
    path('login/', views.login),
    path('register/', views.register),
	path('forgotpsw/', views.forgotpsw),
    path('logout/', views.logout),
	path('captcha/', include('captcha.urls')),
	path('confirm/',views.user_confirm),
	path('psw_reset/', views.psw_reset),
	path('confer_manage/',include('apps.confer_manage.urls')),
	path('sharing/',include('apps.sharing.urls')),
	path('comments/',include('apps.comments.urls')),
##　以下是新增
	re_path(r'^static/(?P<path>.*)$', static.serve,
      {'document_root': settings.STATIC_ROOT}, name='static'),
	#以下新增上传图像用
	re_path(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
# 图片验证码 路由
    path('refresh_captcha/', views.refresh_captcha),
	# sharing
	path('search/', include('haystack.urls')),
	path('notifications/', include(notifications.urls, namespace='notifications')),

]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)