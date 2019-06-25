#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: urls.py
@time: 2019/05/25
"""

from django.urls import path
from . import views

app_name = 'confer_manage'

urlpatterns = [
	path('edit/', views.edit, name='edit'),
	path('userprofile/', views.userprofile, name='userprofile'),
	path('create/', views.create, name='create'),
	path('createajax/', views.createajax, name='createajax'),
	path('editajax/', views.editajax, name='editajax'),
	# path('editcountajax/', views.editcountajax, name='editcountajax'),
	# path('create/', views.create, name='create'),
	path('start/', views.start, name='start'),
	path('chospeople/', views.chospeople, name='chospeople'),
	path('savenewedit/', views.savenewedit, name='savenewedit'),
	path('dashboard/', views.dashboard, name='dashboard'),
	path('usertask/', views.usertask, name='usertask'),
	path('document/', views.document, name='document'),
	path('newdocument/', views.newdocument, name='newdocument'),
	path('choscoonf/', views.choscoonf, name='choscoonf'),
	path('getSubData/', views.getSubData),
	path('getTimeData/', views.getTimeData),
	# path('dropconfer/',views.dropconfer),
	# path('detail/<int:asset_id>/', views.detail, name='detail'),
	# path('', views.dashboard),
]
