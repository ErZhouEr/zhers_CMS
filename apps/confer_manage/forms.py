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


# from . import views  应该是不能互相导入


# users = lg_models.User.objects.filter(has_confirmed=1)
# user_lst = []
# for i in users:
# 	user_lst.append((i.id, i.name))
# print(user_lst)


class ConferForm(forms.Form):
	projects = models.Project.objects.all()
	project_lst = []
	for i in projects:
		project_lst.append((i.id, i.projname))
	#
	# users = lg_models.User.objects.filter(has_confirmed=1)
	# user_lst = []
	# for i in users:
	# 	user_lst.append((i.id, i.name))
	# 放在这里也不行，数据库删除了用户之后，系统不会更新数据，因为只执行了一次这个文件貌似

	conferproj = forms.CharField(label="所属项目", max_length=20, widget=forms.TextInput(
		attrs={'class': 'form-control create-project','placeholder':'*必填 没有可以填无，可选项目：' + str(project_lst), 'autofocus': ''}))
	confersub = forms.CharField(label="会议主题", max_length=20, widget=forms.TextInput(
		attrs={'class': 'form-control create-project', 'placeholder': "请输入会议主题", 'autofocus': ''}))
	people = forms.CharField(widget=forms.SelectMultiple(
		attrs={'class': 'form-control select2 create-project', 'multiple': 'multiple', 'id':'people_selec','data-placeholder': '点击选择参会人员'}))
	stime = forms.CharField(label="会议时间", max_length=50, widget=forms.TextInput(
		attrs={'class': 'form-control pull-right create-project', 'id': "reservationtime", 'autofocus': ''}))

	def __init__(self,*args,**kwargs):
		super(ConferForm, self).__init__(*args,**kwargs)
		# projects = models.Project.objects.all()
		# project_lst = []
		# for i in projects:
		# 	project_lst.append((i.id, i.projname))
		# self.fields['conferproj'].widget.attrs.placeholder = '*必填 没有可以填无，可选项目：' + str(project_lst)
		users = lg_models.User.objects.filter(has_confirmed=1)
		user_lst = []
		for i in users:
			user_lst.append((i.id, i.name))
		print('1', user_lst)
		self.fields['people'].widget.choices = user_lst


class EditForm(forms.Form):
	subjectname = forms.CharField(label="项目名称", max_length=20, widget=forms.TextInput(
		attrs={'class': 'form-control edit-project', 'placeholder': "请输入标准项目名称，不要自由发挥"}))
	subcontent = forms.CharField(label="汇报内容", max_length=50, widget=forms.Textarea(
		attrs={'class': 'form-control edit-project', 'rows': 3, 'placeholder': "请不要超过50字，参考格式1、...；2、...；..."}))
	sharecontent = forms.CharField(label="分享内容", max_length=100, widget=forms.Textarea(
		attrs={'class': 'form-control edit-project', 'id':'share', 'rows': 2, 'placeholder': "请不要超过100字，参考格式1、...；2、...；..."}))
	pretime = forms.CharField(label="预计时间", max_length=10,
	                          widget=forms.TextInput(
		                          attrs={'class': 'form-control edit-project', 'id':'pretime','placeholder': "*必填 （填写数字即可，单位：分钟）"}))
	exreason = forms.CharField(label="超时原因", max_length=30,
	                           widget=forms.TextInput(
		                           attrs={'class': 'form-control edit-project', 'id':'exreason','placeholder': "请不要超过30字，规定时长为3分钟"}))


class StartForm(forms.Form):
	subcontent = forms.CharField(label="汇报内容", max_length=300, widget=forms.Textarea(
		attrs={'class': 'form-control', 'id': 'subcontent', 'rows': 8, 'placeholder': "请不要超过300字，参考格式1、...；2、...；..."}))
	sharecontent = forms.CharField(label="分享内容", max_length=200, widget=forms.Textarea(
		attrs={'class': 'form-control', 'id': 'sharecontent', 'rows': 3,
		       'placeholder': "请不要超过200字，参考格式1、...；2、...；..."}))
	pretime = forms.CharField(label="预计时间", max_length=6,
	                          widget=forms.TextInput(
		                          attrs={'class': 'form-control', 'id': 'pretime', 'readonly': 'readonly',
		                                 'placeholder': "填写数字即可，单位：分钟"}))
	realtime = forms.CharField(label="实际时间", max_length=8,
	                           widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'realtime'}))
	followup = forms.CharField(label="followup", max_length=100,
	                           widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'followup','rows': 2}))
	backup = forms.CharField(label="backup", max_length=100,
	                         widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'backup'}))


class Document(forms.Form):
	conferconclusion = forms.CharField(label="汇报内容", max_length=2000, widget=forms.Textarea(
		attrs={'class': 'form-control', 'id': 'confconclusion', 'rows': 23, 'readonly': 'readonly',
		       'placeholder': "请不要超过1000字，参考格式1、...；2、...；..."}))
