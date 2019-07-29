#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: adminx.py
@time: 2019/07/29
"""
import xadmin
from .models import *

class ConferAdmin(object):
	# 展示的字段
	list_display = ['id', 'confer_type', 'confer_proj','subject', 'process','stime', 'creater','people', 'is_over']
	# 按文章名进行搜索
	search_fields = ['subject']
	# 筛选
	list_filter = ['confer_type', 'creater']

	# 修改默认排序
	ordering = ['-id']

	# 设置只读字段
	readonly_field = ['']

	# 不显示某一字段
	exclude = ['']

	list_display_link = ['id']

# style_fields = {'body':'ueditor'}


class TopicAdmin(object):
	list_display = ['id', 'sentence', 'share', 'confer_id', 'people_id']
	search_fields = ['people_id']
	model_icon = 'fa fa-briefcase'


class FundAdmin(object):
	list_display = ['id', 'fund_apart', 'reason', 'money', 'income_confer', 'income_people', 'is_money_sub']
	search_fields = ['income_people']
	model_icon = 'fa fa-tags'


class ProjAdmin(object):
	list_display = ['id', 'projname']
	search_fields = ['projname']


xadmin.site.register(Conference,ConferAdmin)
xadmin.site.register(Topic,TopicAdmin)
xadmin.site.register(Fund,FundAdmin)
xadmin.site.register(Project,ProjAdmin)