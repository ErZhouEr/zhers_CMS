from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.contrib import messages

import json
from datetime import datetime, timedelta, timezone
import re
import ast
import traceback

from . import models
from . import forms
from apps.login import models as lg_models
from apps.login import forms as lg_forms

from django.views.decorators.csrf import csrf_exempt

import requests

import logging

# logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('django')


# handler = logging.FileHandler("log.txt",encoding='utf-8')
# handler.setLevel(logging.INFO)
# formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)


# Create your views here.


def dashboard(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	cu_user = request.session['user_id']
	people = lg_models.User.objects.get(id=cu_user)
	# 计算基金总金额
	topics = models.Topic.objects.filter(is_ex=1)
	# 根据金额的正负判断收入支出
	income_funds = models.Fund.objects.filter(fund_apart=people.apartment, money__gt=0)
	print(income_funds)
	logger.info(['dashboard:收入项目-', income_funds])
	outcome_funds = models.Fund.objects.filter(fund_apart=people.apartment, money__lt=0)
	logger.info(['dashboard:支出项目-', outcome_funds])
	total_dict = {'income': {}, 'outcome': {}}
	for income in income_funds:
		total_dict['income'][income.income_people.name] = round(total_dict['income'].get(income.income_people.name,
		                                                                                 0) + round(income.money, 1), 1)
	for outcome in outcome_funds:
		total_dict['outcome'][outcome.reason] = round(total_dict['outcome'].get(outcome.income_people.name, 0) + round(
			-outcome.money, 1), 1)
	logger.info(['dashboard:总体收支-', total_dict])
	# money_dict = {}
	# for topic in topics:
	# 	money_dict[topic.people_id.name] = money_dict.get(topic.people_id.name, 0) + topic.money
	# print(money_dict)
	money_type = ['收入', '支出']
	income_people = list(total_dict['income'].keys())
	outcome_people = list(total_dict['outcome'].keys())
	total_data_x = ['收入', '支出']
	for i in income_people:
		if i not in total_data_x:
			total_data_x.append(i)
	for i in outcome_people:
		if i not in total_data_x:
			total_data_x.append(i)
	logger.info(['dashboard:人员-', total_data_x])
	# 收支情况
	layer1_money = {'income': 0, 'outcome': 0}
	for i in total_dict['income']:
		layer1_money['income'] = layer1_money['income'] + total_dict['income'][i]
	for i in total_dict['outcome']:
		layer1_money['outcome'] = abs(layer1_money['outcome']) + abs(total_dict['outcome'][i])
	layer1_money['income'] = round(layer1_money['income'], 1)
	layer1_money['outcome'] = round(layer1_money['outcome'], 1)

	# 找到没交清钱的，进行提醒
	money_notsub = models.Fund.objects.filter(fund_apart=people.apartment, is_money_sub=0, money__gt=0)
	notsub_dict = {}
	for tpc in money_notsub:
		key = tpc.income_people.name + '：在' + tpc.income_confer.stime + '-' + tpc.income_confer.confer_type.confer_type + '中，' + tpc.reason + '(id' + str(
			tpc.id) + ')'
		notsub_dict[key] = round(tpc.money - tpc.money_sub, 2)
	logger.info(['dashboard:欠款项目-', notsub_dict])
	# 统计每个人的会议总数
	people_lst = lg_models.User.objects.all()
	peop_cf_dict = {}
	for peop in people_lst:
		con_num = models.Conference.objects.filter(people=peop).count()
		peop_cf_dict[peop.name] = con_num
	peoples = list(peop_cf_dict.keys())
	values = list(peop_cf_dict.values())
	return render(request, 'confer_manege/dashboard.html', locals())


@csrf_exempt
def huanqian(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	ret = {"status": None, "message": None}
	if request.method == "POST":
		try:
			cu_user = request.session['user_id']
			user = lg_models.User.objects.get(id=cu_user)
			if user.role == 'moneyadmin' or user.role == 'admin':
				item = request.POST.get('item')
				money = request.POST.get('money')
				print(item, money)
				itemlst = item.split('：在', 1)
				people = itemlst[0]
				fundinfo = itemlst[1].split('中，', 1)[1]
				pattern = re.compile('\(id(?P<id>\d+)\)')  # 这个正则的用法比较高级
				fund_id = re.search(pattern, fundinfo).group('id')
				print(fund_id)
				fund = models.Fund.objects.get(id=fund_id)
				fund.money_sub = fund.money
				fund.is_money_sub = True
				fund.save()
				ret['status'] = '成功'
				return HttpResponse(json.dumps(ret))
			else:
				ret['message'] = 'Sorry,你没有权限进行基金操作'
				return HttpResponse(json.dumps(ret))
		except:
			ret['message'] = '后台错误，请联系管理员'
			return HttpResponse(json.dumps(ret))


def addmoneyitem(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	ret = {"status": None, "message": None}
	cu_user = request.session['user_id']
	user = lg_models.User.objects.get(id=cu_user)
	if request.method == "POST":
		data=request.POST
		logging.info(['additem',data])
		print(data)
		fund=models.Fund()
		fund.reason=data.get('reason','')
		try:
			if data.get('type')=='支出':
				fund.money=-1*float(data.get('money',0))
				fund.money_sub=-1*float(data.get('moneysub',0))
				if fund.money==fund.money_sub:
					fund.is_money_sub=True
				else:
					fund.is_money_sub=False
			else:
				fund.money = float(data.get('money', 0))
				fund.money_sub = float(data.get('moneysub', 0))
				if fund.money==fund.money_sub:
					fund.is_money_sub=True
				else:
					fund.is_money_sub=False
			fund.income_people=user
			fund.fund_apart=user.apartment
			print(data.get('confer'))
			if data.get('confer','无')=='无':
				confer=models.Conference.objects.get(id=1)
				print(confer)
				fund.income_confer=confer
			fund.save()
			ret['status']='success'
			return HttpResponse(json.dumps(ret))
		except:
			logging.error(traceback.format_exc(),exc_info=True)
			return HttpResponse(json.dumps(ret))




def usertask(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	cu_user = request.session['user_id']
	conferences = models.Conference.objects.filter(people=cu_user)
	length = len(conferences)
	# 不同类型会议对应不同的颜色
	type_color = {
		'普通小型会议': '#00a65a',
		'紧急小型会议': '#f39c12',
		'项目例会': '#00c0ef',
		'部门例会': '#3c8dbc',
		'紧急部门会议': '#dd4b39'
	}
	confer_data = []
	for confer in conferences:
		confer_dict = {}
		confer_dict['id'] = confer.id
		confer_dict['title'] = confer.confer_type.confer_type
		confer_dict['start'] = datetime.strptime(confer.stime, '%Y/%m/%d %I:%M %p')
		confer_dict['day'] = confer_dict['start'].day
		confer_dict['month'] = confer_dict['start'].month
		confer_dict['year'] = confer_dict['start'].year
		confer_dict['hour'] = confer_dict['start'].hour
		confer_dict['min'] = confer_dict['start'].minute
		confer_dict['second'] = confer_dict['start'].second
		confer_dict['end'] = datetime.strptime(confer.endtime, '%Y/%m/%d %I:%M %p')
		confer_dict['end_day'] = confer_dict['end'].day
		confer_dict['end_month'] = confer_dict['end'].month
		confer_dict['end_year'] = confer_dict['end'].year
		confer_dict['end_hour'] = confer_dict['end'].hour
		confer_dict['end_min'] = confer_dict['end'].minute
		confer_dict['backgroundColor'] = type_color[confer.confer_type.confer_type]
		confer_dict['borderColor'] = type_color[confer.confer_type.confer_type]
		confer_data.append(confer_dict)
	logger.info(['usertask:会议数据-', confer_data])
	return render(request, 'confer_manege/usertask.html', locals())


# def dropconfer(request):
# 	if not request.session.get('is_login', None):
# 		return redirect('/login/')
# 	return render(request,'confer_manege/edit.html')


def create(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	conftype = request.GET.get('confertype')
	confid = request.GET.get('conferid')
	conferstartime = request.GET.get('startime')
	conferstartime = str(conferstartime).replace('000', '', 1)
	formated_stime = datetime.utcfromtimestamp(float(conferstartime)).strftime('%Y/%m/%d %I:%M %p')
	logger.info(['create:开始时间', conferstartime, formated_stime])
	conferendtime = request.GET.get('endtime')
	conferendtime = str(conferendtime).replace('000', '', 1)
	formated_endtime = datetime.utcfromtimestamp(float(conferendtime)).strftime('%Y/%m/%d %I:%M %p')
	# print(conftype,conferstartime,conferendtime)
	users = lg_models.User.objects.filter(has_confirmed=1)
	cu_user = request.session['user_id']
	one_people = lg_models.User.objects.get(id=cu_user)
	# 查询此会议是否是当前登录人创建，只有是登录人创建，并且会议没有被提交过，才会进入会议创建流程
	type_id = models.Sysconf.objects.get(confer_type=conftype)
	logger.info(['create:会议、结束时间及登录人', confid, type_id, formated_stime, one_people])
	try:
		confer = models.Conference.objects.get(id=confid)
		confer_creater = confer.creater.id
		confer_id = confer.id
		confer_is_over = confer.is_over
		if confer_is_over is True:
			request.session['confer_id'] = confer_id
			notice = '所选会议已结束，可以查看会议纪要'
			logger.info(['create:点击会议', notice])
			return document(request)
		# 显示会议的准备进度
		people_count = confer.people.count()
		processed = confer.process
		process = "%.2f%%" % (processed / people_count * 100)
		if processed == people_count:
			start_flag = True
		else:
			start_flag = False
	except:
		confer = None
		confer_creater = None  # 空说明没有这个会议，是新建的
		confer_id = None

	if confer_id is None:
		flag_conf = False  # 未创建的会议
	else:
		flag_conf = True

	if (confer_creater is None) or (confer_creater == cu_user):
		flag_creat = True  # 登录人即创建人
	else:
		flag_creat = False
	# 判断当前登录人是否已经编辑汇报内容
	try:
		topic = models.Topic.objects.get(confer_id=confer_id, people_id=cu_user)
	except:
		topic = None
	if topic is None:
		flag_topic = False  # 未创建的汇报
	else:
		flag_topic = True
	logger.info(['create:各种flag', confer, flag_conf, flag_creat, flag_topic])

	# 在服务端session中添加key认证，避免用户重复提交表单
	token = '10000'  # 可以采用随机数
	request.session['createToken'] = token
	request.session['conftype'] = conftype
	request.session['confer_id'] = confer_id
	request.session['confstime'] = formated_stime
	request.session['confendtime'] = formated_endtime
	logger.info(['create:结束时间', formated_endtime])

	# 在input中显示已提交过的信息
	if confer is not None:
		peoples = confer.people.all()
		names = [people.name for people in peoples]
		data = {'conferproj': confer.confer_proj, 'confersub': confer.subject, 'people': str(names),
		        'stime': confer.stime + ' - ' + confer.endtime}
		logger.info(['create:渲染数据', data])
		startime = confer.stime
		endtime = confer.endtime
		confer_form = forms.ConferForm(auto_id=True, data=data)
	else:
		project = None
		subject = None
		peoples = None
		startime = formated_stime
		endtime = formated_endtime
		data = {'stime': startime + ' - ' + endtime}
		confer_form = forms.ConferForm(auto_id=True, data=data)

	if topic is not None:
		topic_data = {}
		topic_data['sentence'] = ast.literal_eval(topic.sentence)
		topic_num = len(topic_data['sentence'])
		proj_titles = list(topic_data['sentence'].keys())
		proj_content = list(topic_data['sentence'].values())
		topic_data['sharecontent'] = topic.share
		topic_data['pretime'] = topic.pre_time
		topic_data['exreason'] = topic.ex_reason
		print(topic_data)
	else:
		topic_data = None
		topic_num = 0

	edit_Form = forms.EditForm(auto_id=True, data=topic_data)
	return render(request, 'confer_manege/edit.html', locals())


def createajax(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	if request.method == "GET":
		confer_form = forms.ConferForm()
		return render(request, "confer_manege/edit.html", {"obj": confer_form})
	elif request.method == "POST":
		confer_form = forms.ConferForm(request.POST)
		ret = {"status": None, "message": None}
		if confer_form.is_valid():
			# 判断是否是第一次提交
			confertype = request.session['conftype']
			type_id = models.Sysconf.objects.get(confer_type=confertype).id
			cu_user = request.session.get('user_id', None)
			conferstime = request.session.get('confstime', None)
			conferendtime = request.session.get('confendtime', None)
			confer_id = request.session.get('confer_id', None)
			logger.info(['createajax:', confer_id])

			# conference = models.Conference.objects.get(confer_type=type_id, )
			# print("31----", confer_form.cleaned_data)
			# 防止重复提交
			client_token = request.POST.get('createtoken')
			server_token = request.session.get('createToken', None)
			# print(client_token,server_token,client_token==server_token)
			if client_token == server_token:
				try:
					logger.info(['createajax2:', confer_id])
					confer = models.Conference.objects.get(id=int(confer_id))
				except:
					confer = None
				if confer is not None:
					confersub = confer_form.cleaned_data.get('confersub')
					conferproj = confer_form.cleaned_data.get('conferproj')
					# 正则表达式解析多选的参会人员
					conferpeople = confer_form.cleaned_data.get('people')
					pattern = re.compile('\d+')
					people_id_lst = re.findall(pattern, conferpeople)
					confertime = confer_form.cleaned_data.get('stime')
					# peoplelst = conferpeople.split(',')
					startime, endtime = confertime.split('-')
					startime = startime.strip()
					endtime = endtime.strip()
					if len(people_id_lst) < 2:
						ret["message"] = '会议人数太少，请继续添加~'
						return HttpResponse(json.dumps(ret))
					cf_type = models.Sysconf.objects.get(confer_type=confertype)
					try:
						cf_proj = models.Project.objects.get(projname=conferproj)
					except:
						cf_proj = None
					confer.confer_type = cf_type
					confer.confer_proj = cf_proj
					confer.subject = confersub
					confer.stime = startime
					confer.endtime = endtime

					# 多对多方式的数据插入，需要set
					confer_people = []
					for i in people_id_lst:
						confer_people.append(int(i))
					peopleset = lg_models.User.objects.filter(id__in=confer_people)
					confer.people.set(peopleset)
					# 多对多添加会议部门信息
					confer_apart_lst = []
					for i in peopleset:
						confer_apart_lst.append(i.apartment)
					confer.confer_apart.set(confer_apart_lst)
					confer.save()
					ret["message"] = '会议更新成功~'
					ret["status"] = "成功"
					# print("35", ret)
					del request.session['createToken']
					return HttpResponse(json.dumps(ret))
				else:
					# insert new conference
					confersub = confer_form.cleaned_data.get('confersub')
					conferproj = confer_form.cleaned_data.get('conferproj')
					# 正则表达式解析多选的参会人员
					conferpeople = confer_form.cleaned_data.get('people')
					pattern = re.compile('\d+')
					people_id_lst = re.findall(pattern, conferpeople)
					confertime = confer_form.cleaned_data.get('stime')
					# peoplelst = conferpeople.split(',')
					startime, endtime = confertime.split(' - ')
					nowtime = datetime.now().strftime('%Y/%m/%d %I:%M %p')
					if len(people_id_lst) < 2:
						ret["message"] = '会议人数太少，请继续添加~'
						return HttpResponse(json.dumps(ret))
					# elif int(endtime)-int(startime)<0:   #还要判断日期大于当前日期
					#	message='会议时间有误，请再检查下~'
					# return render(request, 'confer_manege/edit.html', locals())
					try:
						cf_type = models.Sysconf.objects.get(confer_type=confertype)
						try:
							cf_proj = models.Project.objects.get(projname=conferproj)
						except:
							cf_proj = None
						cf_creater = lg_models.User.objects.get(id=cu_user)
						newconfer = models.Conference()
						newconfer.confer_type = cf_type
						newconfer.confer_proj = cf_proj
						newconfer.subject = confersub
						newconfer.creater = cf_creater
						newconfer.stime = startime  # 写入的是时间选择框中的开始时间和结束时间
						newconfer.endtime = endtime
						newconfer.creatime = nowtime
						newconfer.save()
						# 多对多方式的数据插入，需要set
						confer_people = []
						for i in people_id_lst:
							confer_people.append(int(i))
						peopleset = lg_models.User.objects.filter(id__in=confer_people)
						newconfer.people.set(peopleset)

						# 多对多添加会议部门信息
						confer_apart_lst = []
						for i in peopleset:
							confer_apart_lst.append(i.apartment)
						newconfer.confer_apart.set(confer_apart_lst)
						newconfer.save()

						request.session['confer_id'] = newconfer.id

						ret["message"] = '会议创建成功，请在下方继续填写你的会议发言资料~'
						ret["status"] = "成功"
						if confertype == '部门例会':
							msg = '[会议通知]' + cf_creater.name + '发起会议，时间为：' + startime + '，请大家提前进入(http://192.168.1.209:8080/ )编辑提交会议汇报内容，并按时参加，谢谢！'
							msg2dingding('text', msg, [], 1)
						# print("35", ret)
						del request.session['createToken']
					except:
						traceback.print_exc()
						logging.error(traceback.format_exc(), exc_info=True)
						ret["message"] = '会议创建失败~'
						ret["status"] = "失败"
					return HttpResponse(json.dumps(ret))
			else:
				ret["message"] = '请勿重复提交~'
				return HttpResponse(json.dumps(ret))
		else:
			# err = obj.errors
			ret["message"] = str(confer_form.errors)
			logger.warning(['create:结束时间', confer_form.errors])
			return HttpResponse(json.dumps(ret))


@csrf_exempt
def editajax(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	if request.method == "GET":
		edit_form = forms.EditForm()
		return render(request, "confer_manege/edit.html", {"obj": edit_form})
	elif request.method == "POST":
		# edit_form = forms.EditForm()
		ret = {"status": None, "message": None}
		n = int(request.POST.get('num',0))
		print(n)
		data = {}
		sentence = {}
		for i in range(n):
			titleid = 'selectproj%s' % str(i + 1)
			title = request.POST.get(titleid)
			contentid = 'contproj%s' % str(i + 1)
			content = request.POST.get(contentid)
			sentence[title] = content
			print(sentence)
		data['sen'] = sentence
		data['share'] = request.POST.get('share', '')
		data['pretime'] = request.POST.get('pretime', '')
		data['exreason'] = request.POST.get('exreason', '')
		logger.info(['editajax:提交数据', data])
		# topic_num = int((len(data) - 3) / 2)

		# insert new conference
		logger.info(['editajax:话题数', n])
		newtopic = models.Topic()
		# sentence = {}
		# for i in range(topic_num):
		# print(i,data[2*i],data[2*i+1])
		#	sentence[data[2 * i]] = data[2 * i + 1]
		cu_user = request.session.get('user_id')
		cu_conf = request.session.get('confer_id')
		try:
			topic = models.Topic.objects.get(people_id=cu_user, confer_id=cu_conf)
		except:
			topic = None
		if topic is not None:
			try:
				# 更新已存在的topic
				topic.sentence = data['sen']
				topic.share = data['share']
				topic.pre_time = data['pretime']
				topic.ex_reason = data['exreason']
				topic.save()
				request.session['topic_id'] = newtopic.id
				ret["message"] = '汇报内容更新成功~'
				ret["status"] = "成功"
			except:
				logging.error(traceback.format_exc(), exc_info=True)
				ret["message"] = '汇报内容更新失败~'
		else:
			try:
				# 新增topic记录，同时更新会议的准备情况（多一个人ready）
				newtopic.sentence = data['sen']
				newtopic.share = data['share']
				newtopic.pre_time = data['pretime']
				newtopic.ex_reason = data['exreason']
				newtopic.is_prepared = True
				newtopic.people_id = lg_models.User.objects.get(id=cu_user)
				confer = models.Conference.objects.get(id=cu_conf)
				newtopic.confer_id = confer
				newtopic.save()
				# 尝试计算会议准备进度
				people_count = confer.people.count()
				confer.process = confer.process + 1
				process = "%.2f%%" % (confer.process / people_count * 100)
				confer.save()
				ret['process'] = process
				request.session['topic_id'] = newtopic.id
				ret["message"] = '汇报内容编辑成功~'
				ret["status"] = "成功"
			except:
				ret["message"] = '汇报内容编辑失败~'
		logger.info(['editajax:编辑结果', ret])

		# del request.session['createToken']
		return HttpResponse(json.dumps(ret))


def edit(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	if request.method == 'POST':
		edit_Form = forms.EditForm(request.POST)
		message = "请检查填写的内容！"
		if edit_Form.is_valid():
			subjectname = edit_Form.cleaned_data.get('subjectname')
			subcontent = edit_Form.cleaned_data.get('subcontent')
			pretime = edit_Form.cleaned_data.get('pretime')
			exreason = edit_Form.cleaned_data.get('exreason')

			# newtopic=models.Topic()
			# newtopic.sentence=str({'subject':subjectname,'content':subcontent})
			# newtopic.pre_time=pretime
			# newtopic.ex_reason=exreason
			# newtopic.people_id=request.session.get('user_id')
			# newtopic.confer_id=request.session.get('confer_id')
			#
			# newtopic.save()
			#
			# request.session['topic_id'] = newtopic.id

			return render(request, 'confer_manege/edit.html', locals())
		else:
			return render(request, 'confer_manege/edit.html', locals())
	edit_Form = forms.EditForm(auto_id=True)
	confer_form = forms.ConferForm(auto_id=True)
	return render(request, 'confer_manege/edit.html', locals())


def start(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	confer_id = request.session['confer_id']
	cu_user = request.session['user_id']
	confer = models.Conference.objects.get(id=confer_id)
	people = confer.people.all()
	people_lst = []
	for i in people:
		people_lst.append(i.name + ' / ' + i.email)
	logger.info(['start:会议及人员', confer, people_lst])
	try:
		topic = models.Topic.objects.get(confer_id=confer_id, people_id=cu_user)
		sentence = ''
		sen_dict = ast.literal_eval(topic.sentence)
		for key in sen_dict.keys():
			sentence = sentence + key + ':' + '\n' + sen_dict[key] + '\n' + '-----' * 10 + '\n'
		data = {'subcontent': sentence, 'sharecontent': topic.share, 'pretime': topic.pre_time * 60,
		        "realtime": topic.real_time, "followup": topic.followup}
		start_form = forms.StartForm(auto_id=True, data=data)
	except:
		logger.error(['start:会议及人员', confer, people_lst], exc_info=True)
		data = {'subcontent': '无', 'sharecontent': '无', 'pretime': '无',
		        "realtime": '无', "followup": '无'}
		start_form = forms.StartForm(auto_id=True, data=data)
	return render(request, 'confer_manege/start.html', locals())


@csrf_exempt
def chospeople(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	confer_id = request.session['confer_id']
	cu_user = request.session['user_id']
	ret = {"status": '失败', "message": '请检查输入'}
	if request.method == 'POST':
		email = request.POST.get('people').split('/')[1].strip()
		people = lg_models.User.objects.get(email=email)
		logger.info(['choose people:', people.name, confer_id])
		# print(confer_id,people)
		try:
			topic = models.Topic.objects.get(confer_id=confer_id, people_id=people)
			logger.info(['choose topic:', topic.sentence])
			sentence = ''
			sen_dict = ast.literal_eval(topic.sentence)
			for key in sen_dict.keys():
				sentence = sentence + key + ':' + '\n' + sen_dict[key] + '\n' + '-----' * 10 + '\n'
			data = {"subcontent": sentence, "sharecontent": topic.share, "pretime": topic.pre_time * 60,
			        "realtime": topic.real_time, "followup": topic.followup, "status": '成功', "message": '选择成功！'}
		except:
			topic = None
			logger.error(['choose topic:', people.name, confer_id], exc_info=True)
			data = {"status": '失败', "message": '无数据！'}
		return HttpResponse(json.dumps(data))

	return HttpResponse(json.dumps(ret))


@csrf_exempt
def savenewedit(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	ret = {"status": '失败', "message": '请检查输入'}
	if request.method == 'POST':
		data = request.POST
		logging.info(['newdata', data])
		# print(data)
		email = data['peop'].split('/')[1].strip()
		people = lg_models.User.objects.get(email=email)
		confer_id = request.session['confer_id']
		confer = models.Conference.objects.get(id=confer_id)
		logger.info(['savenewedit', people, confer_id])
		try:
			topic = models.Topic.objects.get(confer_id=confer_id, people_id=people)
		except:
			topic = models.Topic()
			topic.confer_id = confer
			topic.people_id = people
		try:
			sen_dict = {}  # 这部分字符串处理的还是不够灵活啊
			sentence = data['sentence']
			topicsubs = sentence.split('-----' * 10)
			print(topicsubs)
			logger.info(['savenewedit', topicsubs])
			for sub in topicsubs:
				sub = sub.strip('-')
				if len(sub) > 5:
					logger.info(['savenewedit', sub])
					sen_lst = sub.split(':')
					logger.info(['savenewedit', sen_lst])
					sen_dict[sen_lst[0].strip()] = sen_lst[1].strip()
			topic.sentence = sen_dict
			topic.share = data['share']
			topic.real_time = data['rtime']
			if (topic.pre_time is not None) and (topic.pre_time>3):
				if int(data['rtime']) - 60 *topic.pre_time>0:
					topic.is_ex = True
					topic.ex_time = int(data['rtime']) - 60 *topic.pre_time
			elif int(data['rtime']) - 60 * 3 > 0:
				topic.is_ex = True
				topic.ex_time = int(data['rtime']) - 60 * 3
			else:
				topic.is_ex = False
			if topic.is_ex:
				try:
					fund = models.Fund.objects.get(income_confer=confer, income_people=people, reason='发言超时')
					fakuan = (topic.ex_time) * 0.1
					topic.money = fakuan
					fund.money = fakuan
					fund.save()
				except:
					newfund = models.Fund()
					fakuan = (topic.ex_time) * 0.1
					topic.money = fakuan
					newfund.money = fakuan
					newfund.fund_apart = people.apartment
					newfund.reason = '发言超时'
					newfund.income_people = people
					newfund.income_confer = confer
					newfund.save()

			else:
				try:
					# 这里是防止一开始时间计算错误，导致超时，后来修改的时候把罚款改为0
					fund = models.Fund.objects.get(income_confer=confer, income_people=people, reason='发言超时')
					fund.money = 0
					fund.save()
				except:
					pass
				topic.ex_time = 0
				topic.money = 0
			if not topic.is_prepared:
				if not models.Fund.objects.filter(income_confer=confer, income_people=people,
				                                  reason='未提交汇报摘要').exists() and people.name != 'David':
					newfund = models.Fund()
					newfund.money = 5
					newfund.fund_apart = people.apartment
					newfund.reason = '未提交汇报摘要'
					newfund.income_people = people
					newfund.income_confer = confer
					newfund.save()
			else:
				try:
					# 这里是防止外部用户的topic虽然提交了，但是is_prepared是false的状态
					fund = models.Fund.objects.get(income_confer=confer, income_people=people, reason='未提交汇报摘要')
					fund.delete()
				except:
					pass
			topic.followup = data['follup']
			topic.save()
			ret['status'] = '成功'
			ret['message'] = '保存成功'
		except Exception as err:
			topic = None
			print(err.__class__.__name__, err, ';')
			logger.error(traceback.format_exc(), exc_info=True)  # traceback.print_exc()
			ret['message'] = '保存失败，请联系管理员'
		logger.info(ret)

		return HttpResponse(json.dumps(ret))

	return HttpResponse(json.dumps(ret))


def document(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	conf_dict = {}
	conf_types = models.Sysconf.objects.all()
	for typ in conf_types:
		conf_subs = models.Conference.objects.filter(confer_type=typ.id)
		conf_dict_l2 = {}
		for sub in conf_subs:
			confs = models.Conference.objects.filter(confer_type=typ.id, subject=sub.subject)
			conf_times = []
			for conf in confs:
				conf_times.append(conf.stime)
			conf_dict_l2[sub.subject] = conf_times
		conf_dict[typ.confer_type] = conf_dict_l2
	all_types = conf_dict.keys()
	try:
		confer_id = request.session['confer_id']
		cu_user = request.session['user_id']
		confer = models.Conference.objects.get(id=confer_id)
		user = lg_models.User.objects.get(id=cu_user)
		data = {'conferconclusion': confer.confer_conclusion}
	except:
		data = None
	document_form = forms.Document(auto_id=True, data=data)
	return render(request, 'confer_manege/document.html', locals())


def newdocument(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	conf_dict = {}
	conf_types = models.Sysconf.objects.all()
	for typ in conf_types:
		conf_subs = models.Conference.objects.filter(confer_type=typ.id)
		conf_dict_l2 = {}
		for sub in conf_subs:
			confs = models.Conference.objects.filter(confer_type=typ.id, subject=sub.subject)
			conf_times = []
			for conf in confs:
				conf_times.append(conf.stime)
			conf_dict_l2[sub.subject] = conf_times
		conf_dict[typ.confer_type] = conf_dict_l2
	all_types = conf_dict.keys()
	try:
		confer_id = request.session['confer_id']
		cu_user = request.session['user_id']
		confer = models.Conference.objects.get(id=confer_id)
		user = lg_models.User.objects.get(id=cu_user)
		confer_is_over = confer.is_over
		if confer_is_over is True:
			notice = '所选会议已结束，可以查看会议纪要'
			print(notice)
			logging.info(notice)
			return document(request)
		topics = models.Topic.objects.filter(confer_id=confer_id)
		conclusion = {}  # 读取topic中保存的字典并形成会议纪要的格式
		for topic in topics:
			sen_dict = ast.literal_eval(topic.sentence)
			for key in sen_dict:
				# print(key, sen_dict)
				conclusion[key] = conclusion.get(key, [])
				sen_lst = sen_dict[key].split('\n')
				for i in sen_lst:
					conclusion[key].append(
						'* [ ' + topic.people_id.name + ' ] ' + i.replace('\n', ''))  # 有问题啊，用换行符切分是不是好一点
		doc = '【会议纪要】\n'
		for key in conclusion:
			doc = doc + 'PROJECT: ' + key + ':\n' + '\n'.join(conclusion[key]) + '\n'

		share = '【SHARE】\n'
		for topic in topics:
			if len(topic.share) > 3:
				share = share + '* [ ' + topic.people_id.name + ' ] ' + topic.share + '\n'
		follup = '【FOLLOW UP】\n'
		for topic in topics:
			if len(topic.followup) > 3:
				follup = follup + '* [ ' + topic.people_id.name + ' ] ' + topic.followup + '\n'
		money = '【DONATION】\n'
		money_people_lst = ['']
		print(money_people_lst, type(money_people_lst))
		for topic in topics:
			if topic.is_ex is True:
				if topic.is_money_sub is not True:
					status = '待还'
				else:
					status = '已还'
				money = money + '* [ ' + topic.people_id.name + ' ] 发言超时，' + '本次需奉献' + str(
					round(topic.money, 3)) + '元' + '，已奉献' + str(
					topic.money_sub) + '元' + '\n'
				money_people_lst.append(topic.people_id.phone)

		if models.Fund.objects.filter(income_confer=confer_id, reason='未提交汇报摘要').exists():
			funds = models.Fund.objects.filter(income_confer=confer_id, reason='未提交汇报摘要')
			# print(confer_id, funds)
			for fund in funds:
				money = money + '* [ ' + fund.income_people.name + ' ] 未提交汇报摘要，' + '本次需奉献' + str(
					fund.money) + '元' + '，已奉献' + str(
					fund.money_sub) + '元' + '\n'
				money_people_lst.append(fund.income_people.phone)
		else:
			s = '无其他罚款项~\n'
			money = money + s
		foot = '< 会议记录人 > -' + user.name + ' / ' + user.email
		doc = doc + '-----' * 40 + '\n' + share + '-----' * 40 + '\n' + follup + '-----' * 40 + '\n' + money + '-----' * 40 + '\n' + foot
		confer.confer_conclusion = doc
		confer.conclusioner = user
		confer.is_over = True
		confer.save()
		logger.info('会议纪要保存成功')
		msg = '【会议纪要】' + 'http://192.168.1.209:8080/confer_manage/document/' + '，请大家点击链接查看，谢谢！'
		msg2 = money.replace('DONATION', '罚款情况')
		msg2dingding('text', msg, [], 1)
		msg2dingding('text', msg2 + '，请发红包给阿连，谢谢', money_people_lst, 0)
		try:
			former_funds = models.Fund.objects.filter(is_money_sub=False)  # 往期未交清罚款怎么做
			former_money = '【往期滞交罚款】\n'
			former_money_people=[]
			for former_fund in former_funds:
				if former_fund.income_confer_id != confer.id:
					former_money = former_money + '* [ ' + former_fund.income_people.name + ' ] 在往期会议中' + former_fund.reason + '，已交' + str(
						former_fund.money_sub) + '元，仍欠款' +str(former_fund.money-former_fund.money_sub)+'元，请及时交款~\n'
					former_money_people.append(former_fund.income_people.phone)
			msg2dingding('text', former_money + '，请发红包给阿连，谢谢', former_money_people, 0)
		except:
			logging.error(traceback.format_exc(),exc_info=True)
		confer_ownerlst=['连漪','高飘飘','谭子能','伟叔','韩雪','黄晓华','吴任','麦苑菲','周策','杨永健','刘志文']
		data = {'conferconclusion': doc}
		document_form = forms.Document(auto_id=True, data=data)
		return render(request, 'confer_manege/document.html', locals())
	except:
		logging.error(traceback.format_exc(), exc_info=True)
		return render(request, 'confer_manege/500.html', locals())


# ---------------------数据库与前端document页面交互生成前端元素---------------------------
conf_dict = {}
conf_types = models.Sysconf.objects.all()
for typ in conf_types:
	conf_subs = models.Conference.objects.filter(confer_type=typ.id)
	conf_dict_l2 = {}
	for sub in conf_subs:
		confs = models.Conference.objects.filter(confer_type=typ.id, subject=sub.subject)
		conf_times = []
		for conf in confs:
			conf_times.append(conf.stime)
		conf_dict_l2[sub.subject] = conf_times
	conf_dict[typ.confer_type] = conf_dict_l2


# Confer_dict = {
# 	"普通小型会议": {
# 		"啊啊啊啊": ["哈哈", "嘎嘎"],
# 		"噢噢噢噢": ["问问", "嗯嗯", "然然"],
# 		"呜呜呜呜": ["刚刚", "等等", "找找"]
# 	},
# 	"项目例会": {
# 		"练练": ["12", "23", "34"],
# 		"吉吉": []
# 	},
# 	"部门例会": {
# 		"45": [],
# 		"67": []
# 	}
# }
@csrf_exempt
def choscoonf(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	ret = {"status": '失败', "message": '请检查输入'}
	if request.method == 'POST':
		data = request.POST
		# print(data)
		conftype = models.Sysconf.objects.get(confer_type=data['cftyp'])
		confsub = data['cfsb']
		conftime = data['cftm']
		logger.info(['choscoonf:选择会议', conftype, confsub, conftime])
		try:
			conf = models.Conference.objects.get(confer_type=conftype, subject=confsub, stime=conftime)
			conclusion = conf.confer_conclusion
			searchdata = {'conclusion': conclusion, 'status': '成功'}
			ret['status'] = '成功'
			return HttpResponse(json.dumps(searchdata))
		except:
			ret['massage'] = '抱歉，未找到相关会议'
			return HttpResponse(json.dumps(ret))


def getSubData(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	confertype = request.GET['confertype']
	Sub_list = []
	for sub in conf_dict[confertype]:
		Sub_list.append(sub)
	return HttpResponse(json.dumps(Sub_list))


def getTimeData(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	confertype, confersub = request.GET['confertype'], request.GET['confersub']
	Time_list = conf_dict[confertype][confersub]
	return HttpResponse(json.dumps(Time_list))


def userprofile(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	cu_user = request.session['user_id']
	user = lg_models.User.objects.get(id=cu_user)
	name = user.name
	apartment = user.apartment.apartment
	email = user.email
	data = {}
	user_form = lg_forms.editUserForm(data=data)
	return render(request, 'confer_manege/profile.html', locals())


# 上传用户头像
@csrf_exempt
def upload(request):
	if request.method == 'POST':
		user_id = request.session.get('user_id')
		avatar = request.FILES.get('avatar')
		ret = {"status": '失败'}
		try:
			user = lg_models.User.objects.get(id=user_id)
			user.picture = avatar
			user.save()
			# print(avatar)
			request.session['avatar'] = avatar
			print(request.session['avatar'])
			ret['status'] = '成功'
			return HttpResponse(json.dumps(ret))
		except:
			print(traceback.print_exc())
			return HttpResponse(json.dumps(ret))


# else:
# 	return render(request, 'confer_manege/profile.html')


def msg2dingding(msgtype, message, people_lst, flag):
	url = 'https://oapi.dingtalk.com/robot/send?access_token=b0cb9de85f59c94b7c0b914f4b073e82fae2fefc18de252c31dc806e5cd51a1f'  # 钉钉机器人的webhook地址
	HEADERS = {
		"Content-Type": "application/json ;charset=utf-8 "
	}
	message = message
	String_textMsg = {
		"msgtype": msgtype,
		"text": {"content": message},
		"at": {
			"atMobiles": people_lst,
			# 	[
			# 	"18789461193"  # 如果需要@某人，这里写他的手机号
			# ],
			"isAtAll": flag  # 如果需要@所有人，这些写1
		}
	}
	sendData = json.dumps(String_textMsg)
	sendData = sendData.encode("utf-8")  # python3的Request要求data为byte类型
	res = requests.post(url, data=sendData, headers=HEADERS)
	print(res.text)


# 每周四定时钉钉提醒创建会议，这种方法不行，服务启动不了，应该是一直在循环吧
# import time
#
# sched_time = datetime(2019, 7, 25, 15, 0, 0)
# loopflag = 0
# while True:
# 	now = datetime.now()
# 	if sched_time<now<(sched_time+timedelta(seconds=1)):
# 		loopflag = 1
# 		time.sleep(1)
# 		if loopflag == 1:
# 			msg='当前时间为周四下午3点，请本期例会负责人尽快创建会议~'
# 			msg2dingding('text', msg, [], 0) #此处为你自己想定时执行的功能函数
# 			loopflag = 0
# 			sched_time=sched_time+timedelta(days=7)