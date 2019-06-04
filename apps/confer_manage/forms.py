#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: forms.py
@time: 2019/05/25
"""

from django import forms
from . import models
from apps.login import models as lg_models

users = lg_models.User.objects.filter(has_confirmed=1)
user_lst = []
for i in users:
	user_lst.append((i.id, i.name))

projects=models.Project.objects.all()
project_lst = []
for i in projects:
	project_lst.append((i.id, i.projname))


class ConferForm(forms.Form):
	# confertype = forms.CharField(label="会议类型", max_length=20, widget=forms.TextInput(
	# 	attrs={'class': 'form-control', 'placeholder': "请输入会议类型", 'autofocus': ''}))
	conferproj = forms.CharField(label="所属项目", max_length=20, widget=forms.TextInput(
		attrs={'class': 'form-control create-project', 'placeholder': '可选项目：'+str(project_lst), 'autofocus': ''}))
	confersub = forms.CharField(label="会议主题", max_length=20, widget=forms.TextInput(
		attrs={'class': 'form-control create-project', 'placeholder': "请输入会议主题", 'autofocus': ''}))
	# people = forms.CharField(label="参会人员", max_length=50,
	#                          widget=forms.TextInput(
	# 	                         attrs={'class': 'form-control', 'id': 'conferpeople', 'placeholder': "选择参会人员"}))
	people = forms.CharField(widget=forms.SelectMultiple(choices=user_lst,
	                                                attrs={'class': 'form-control select2 create-project', 'multiple': 'multiple',
	                                                       'data-placeholder': '点击选择参会人员'}))
	stime = forms.CharField(label="会议时间", max_length=30, widget=forms.TextInput(
		attrs={'class': 'form-control pull-right create-project', 'id': "reservationtime", 'autofocus': ''}))


class EditForm(forms.Form):
	subjectname = forms.CharField(label="项目名称", max_length=20, widget=forms.TextInput(
		attrs={'class': 'form-control edit-project', 'placeholder': "请输入标准项目名称，不要自由发挥"}))
	subcontent = forms.CharField(label="汇报内容", max_length=50, widget=forms.Textarea(
		attrs={'class': 'form-control edit-project', 'rows': 3, 'placeholder': "请不要超过50字，参考格式1、...；2、...；..."}))
	sharecontent = forms.CharField(label="分享内容", max_length=50, widget=forms.Textarea(
		attrs={'class': 'form-control', 'rows': 2, 'placeholder': "请不要超过50字，参考格式1、...；2、...；..."}))
	pretime = forms.CharField(label="预计时间", max_length=10,
	                          widget=forms.TextInput(
		                          attrs={'class': 'form-control', 'placeholder': "填写数字即可，单位：分钟"}))
	exreason = forms.CharField(label="超时原因", max_length=30,
	                           widget=forms.TextInput(
		                           attrs={'class': 'form-control', 'placeholder': "请不要超过30字，规定时长为3分钟"}))


class StartForm(forms.Form):
	subcontent = forms.CharField(label="汇报内容", max_length=100, widget=forms.Textarea(
		attrs={'class': 'form-control', 'rows': 5, 'placeholder': "请不要超过1000字，参考格式1、...；2、...；..."}))
	realtime = forms.CharField(label="实际时间", max_length=10,
	                           widget=forms.TextInput(attrs={'class': 'form-control'}))
	followup = forms.CharField(label="followup", max_length=30,
	                           widget=forms.TextInput(attrs={'class': 'form-control'}))


class Document(forms.Form):
	conferconclusion = forms.CharField(label="汇报内容", max_length=100, widget=forms.Textarea(
		attrs={'class': 'form-control', 'rows': 20, 'placeholder': "请不要超过1000字，参考格式1、...；2、...；..."}))
