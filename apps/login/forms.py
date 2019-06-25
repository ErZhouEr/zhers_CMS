#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: forms.py
@time: 2019/05/25
"""

from django import forms
from captcha.fields import CaptchaField
from apps.confer_manage.models import Apartment

apartments=Apartment.objects.all()
apartment_lst = []
for i in apartments:
	apartment_lst.append((i.id, i.apartment))


class UserForm(forms.Form):
	username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': "Username", 'autofocus': ''}))
	password = forms.CharField(label="密码", max_length=256,
	                           widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password"}))
	captcha = CaptchaField(label='验证码')


class RegisterForm(forms.Form):
	gender = (
		('male', "男"),
		('female', "女"),
	)
	roles = (
		('user', '普通用户'),
		('moneyadmin', '基金管理员'),
		('admin', "管理员"),
	)

	username = forms.CharField(label="用户名", min_length=2, max_length=10, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': "请输入不少于2位用户名"}))
	password1 = forms.CharField(label="密码", min_length=6, max_length=10, widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': "请输入不少于6位密码"}))
	password2 = forms.CharField(label="确认密码", min_length=6, max_length=10,
	                            widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
	sex = forms.ChoiceField(label='性别', choices=gender)
	apartment = forms.ChoiceField(label='部门', choices=apartment_lst)
	role=forms.ChoiceField(label='角色',choices=roles)
	captcha = CaptchaField(label='验证码')


class editUserForm(forms.Form):
	roles = (
		('user', '普通用户'),
		('moneyadmin', '基金管理员'),
		('admin', "管理员"),
	)
	username = forms.CharField(label="用户名", min_length=2, max_length=10, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': "请输入不少于2位用户名"}))
	password1 = forms.CharField(label="密码", min_length=6, max_length=10, widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': "请输入不少于6位密码"}))
	password2 = forms.CharField(label="确认密码", min_length=6, max_length=10,
	                            widget=forms.PasswordInput(attrs={'class': 'form-control'}))
	email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
	apartment = forms.ChoiceField(label='部门', choices=apartment_lst)
	role=forms.ChoiceField(label='角色',choices=roles)