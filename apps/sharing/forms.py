#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: forms.py
@time: 2019/07/28
"""

from .models import Post,Category,Tag
from django import forms
from mdeditor.fields import MDTextFormField


class PostForm(forms.Form):
	title=forms.CharField(label="标题", max_length=25, widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': "文章标题", 'autofocus': ''}))
	post=MDTextFormField()
	excerpt=forms.CharField(label="标题", max_length=125, widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': "文章摘要", 'autofocus': ''}))
	category=forms.CharField(widget=forms.Select(
		attrs={'class': 'form-control select2', 'data-placeholder': '点击选择类别'}))
	tag=forms.CharField(widget=forms.SelectMultiple(
		attrs={'class': 'form-control select2', 'multiple': 'multiple','data-placeholder': '点击添加标签'}))

	def __init__(self,*args,**kwargs):
		super(PostForm, self).__init__(*args,**kwargs)
		categorys = Category.objects.all()
		cate_lst = []
		for i in categorys:
			cate_lst.append((i.id, i.name))
		self.fields['category'].widget.choices = cate_lst

		tags = Tag.objects.all()
		tag_lst = []
		for i in tags:
			tag_lst.append((i.id, i.name))
		print(tag_lst)
		self.fields['tag'].widget.choices = tag_lst

