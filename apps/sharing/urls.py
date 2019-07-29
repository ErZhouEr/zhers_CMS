#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: urls.py
@time: 2019/06/25
"""

from django.urls import path,include
from . import views
from django.contrib import admin

app_name = 'sharing'

urlpatterns = [
	path('', views.index, name='index'),
	# path('admin/', admin.site.urls,name="admin"),
	path('archives/<int:year>/<int:month>/', views.ArchivesView.as_view(), name='archives'),
	path('post/<int:pk>', views.PostDetailView.as_view(), name='post'),

	#path('categories/', views.Categories.as_view(), name='categories'),
	path('category/<int:pk>', views.CategoryView.as_view(), name='category'),
	#
	path('tag/', views.TagView.as_view(), name='tag'),
	path('tag/<int:pk>', views.TagView.as_view(), name='tag'),
	path('write/', views.write, name='write'),
	path('adddoc/', views.adddoc, name='adddoc'),
	path('savepost/', views.savepost, name='savepost'),
]
