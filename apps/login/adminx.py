#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: adminx.py
@time: 2019/07/29
"""

import xadmin
from .models import User


class UserAdmin(object):
	# 展示的字段
	list_display = ['id', 'name', 'email', 'phone', 'role', 'apartment']
	# 按人名进行搜索
	search_fields = ['name']
	# 筛选
	list_filter = ['id', 'role', 'apartment']

	# 修改默认排序
	ordering = ['-id']

	# 设置只读字段
	readonly_field = ['']

	# 不显示某一字段
	exclude = ['']

	list_display_link = ['name']

xadmin.site.register(User,UserAdmin)