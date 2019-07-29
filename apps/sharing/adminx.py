# -*- coding:utf-8 -*-
import xadmin
from .models import *
from xadmin import views


# 此类可以定义admin后台显示的字段，比如文章列表显示标题，创建时间，
class PostAdmin(object):
    # 展示的字段
    list_display = ['id', 'title', 'created_time', 'category', 'status','excerpt']
    # 按文章名进行搜索
    search_fields = ['title']
    # 筛选
    list_filter = ['id', 'title', 'created_time', 'category', 'status']
    # 修改图标
    model_icon = 'fa fa-bell'
    # 修改默认排序
    ordering = ['-id']

    # 设置只读字段
    readonly_field = ['']

    # 不显示某一字段
    exclude = ['']

    list_display_link = ['title']

    # style_fields = {'body':'ueditor'}


class CategoryAdmin(object):
    list_display = ['id','name']
    search_fields = ['name']
    model_icon = 'fa fa-briefcase'


class TagAdmin(object):
    list_display = ['id', 'name']
    search_fields = ['name']
    model_icon = 'fa fa-tags'



xadmin.site.register(Post,PostAdmin)
xadmin.site.register(Category,CategoryAdmin)
xadmin.site.register(Tag,TagAdmin)