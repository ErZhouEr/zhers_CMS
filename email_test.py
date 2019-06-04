#!usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:l
@file: email_test.py
@time: 2019/05/25
"""


import os
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'piston_CMS.settings'

if __name__ == '__main__':

    subject, from_email, to = '来自会议管理系统的测试邮件', '917846003@qq.com', 'ce.zhou@pistonint.com'
    text_content = '欢迎访问zhce的会议管理系统，这里是数鼎科技分析与建模分队的会议管理站点，欢迎加入，一起愉快的开会！'
    html_content = '<p>欢迎访问<a href="http://127.0.0.1:8000/index/" target=blank>www.piston_meeting.com</a>，这里是数鼎科技分析与建模分队的会议管理站点，欢迎加入，一起愉快的开会！</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()