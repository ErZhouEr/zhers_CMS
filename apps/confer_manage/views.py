from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.contrib import messages

import json
from datetime import datetime, timedelta, timezone
import re
import ast

from . import models
from . import forms
from apps.login import models as lg_models

from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def dashboard(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	topics=models.Topic.objects.filter(is_ex=1)
	money_dict={}
	for topic in topics:
		money_dict[topic.people_id.name]=money_dict.get(topic.people_id.name,0)+topic.money
	print(money_dict)
	money_people=list(money_dict.keys())
	topics_notsub=models.Topic.objects.filter(is_money_sub=0)
	notsub_dict={}
	for tpc in topics_notsub:
		key=tpc.people_id.name+tpc.confer_id.subject
		notsub_dict[key]=tpc.money-tpc.money_sub
	return render(request, 'confer_manege/dashboard.html', locals())


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
		confer_dict['title'] = confer.confer_type.confer_type
		confer_dict['start'] = datetime.strptime(confer.stime, '%Y-%m-%d %H:%M:%S')
		confer_dict['day'] = confer_dict['start'].day
		confer_dict['month'] = confer_dict['start'].month
		confer_dict['year'] = confer_dict['start'].year
		confer_dict['hour'] = confer_dict['start'].hour + 8
		confer_dict['min'] = confer_dict['start'].minute
		confer_dict['second'] = confer_dict['start'].second
		confer_dict['end'] = datetime.strptime(confer.endtime, '%Y-%m-%d %H:%M:%S')
		confer_dict['end_day'] = confer_dict['end'].day
		confer_dict['end_month'] = confer_dict['end'].month
		confer_dict['end_year'] = confer_dict['end'].year
		confer_dict['end_hour'] = confer_dict['end'].hour + 8
		confer_dict['end_min'] = confer_dict['end'].minute
		confer_dict['backgroundColor'] = type_color[confer.confer_type.confer_type]
		confer_dict['borderColor'] = type_color[confer.confer_type.confer_type]
		confer_data.append(confer_dict)
	print(confer_data)
	return render(request, 'confer_manege/usertask.html', locals())


# def dropconfer(request):
# 	if not request.session.get('is_login', None):
# 		return redirect('/login/')
# 	return render(request,'confer_manege/edit.html')


def create(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	conftype = request.GET.get('confertype')
	conferstartime = request.GET.get('startime')
	conferstartime = str(conferstartime).replace('000', '', 1)
	formated_stime = datetime.utcfromtimestamp(float(conferstartime)).strftime('%Y-%m-%d %H:%M:%S')
	print(1, conferstartime, formated_stime)
	conferendtime = request.GET.get('endtime')
	conferendtime = str(conferendtime).replace('000', '', 1)
	formated_endtime = datetime.utcfromtimestamp(float(conferendtime)).strftime('%Y-%m-%d %H:%M:%S')
	# print(conftype,conferstartime,conferendtime)
	users = lg_models.User.objects.filter(has_confirmed=1)
	cu_user = request.session['user_id']
	one_people = lg_models.User.objects.get(id=cu_user)
	# 查询此会议是否是当前登录人创建，只有是登录人创建，并且会议没有被提交过，才会进入会议创建流程
	type_id = models.Sysconf.objects.get(confer_type=conftype)
	print(2, type_id, formated_stime, one_people)
	try:
		confer = models.Conference.objects.get(confer_type=type_id, stime=formated_stime, people=one_people)
		confer_creater = confer.creater.id
		confer_id = confer.id
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
	print(3, confer, flag_conf, flag_creat, flag_topic)

	# 在服务端session中添加key认证，避免用户重复提交表单
	token = '10000'  # 可以采用随机数
	request.session['createToken'] = token
	request.session['conftype'] = conftype
	request.session['confer_id'] = confer_id
	request.session['confstime'] = formated_stime
	request.session['confendtime'] = formated_endtime
	print(4, formated_endtime)

	# 在input中显示已提交过的信息
	if confer is not None:
		data = {'conferproj': confer.confer_proj, 'confersub': confer.subject, 'people': confer.people}
		startime = confer.stime
		endtime = confer.endtime
		confer_form = forms.ConferForm(auto_id=True, data=data)
	else:
		project = None
		subject = None
		peoples = None
		startime = None
		endtime = None
		confer_form = forms.ConferForm(auto_id=True)

	if topic is not None:
		pass

	edit_Form = forms.EditForm(auto_id=True)
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

			# conference = models.Conference.objects.get(confer_type=type_id, )
			# print("31----", confer_form.cleaned_data)
			# 防止重复提交
			client_token = request.POST.get('createtoken')
			server_token = request.session.get('createToken', None)
			# print(client_token,server_token,client_token==server_token)
			if client_token == server_token:
				try:
					confer = models.Conference.objects.get(confer_type=type_id, stime=conferstime, people=cu_user)
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
					if len(people_id_lst) < 2:
						ret["message"] = '会议人数太少，请继续添加~'
						return HttpResponse(json.dumps(ret))
					cf_type = models.Sysconf.objects.get(confer_type=confertype)
					cf_proj = models.Project.objects.get(projname=conferproj)
					confer.confer_type = cf_type
					confer.confer_proj = cf_proj
					confer.subject = confersub
					confer.stime = conferstime
					confer.endtime = conferendtime
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
					print(confer_apart_lst)
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
					startime, endtime = confertime.split('-')
					if len(people_id_lst) < 2:
						ret["message"] = '会议人数太少，请继续添加~'
						return HttpResponse(json.dumps(ret))
					# elif int(endtime)-int(startime)<0:   #还要判断日期大于当前日期
					#	message='会议时间有误，请再检查下~'
					# return render(request, 'confer_manege/edit.html', locals())
					try:
						cf_type = models.Sysconf.objects.get(confer_type=confertype)
						cf_proj = models.Project.objects.get(projname=conferproj)
						cf_creater = lg_models.User.objects.get(id=cu_user)
						# print(type(people_id_lst))
						newconfer = models.Conference()
						newconfer.confer_type = cf_type
						newconfer.confer_proj = cf_proj
						newconfer.subject = confersub
						newconfer.creater = cf_creater
						newconfer.stime = conferstime
						newconfer.endtime = conferendtime
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
						print(confer_apart_lst)
						newconfer.confer_apart.set(confer_apart_lst)
						newconfer.save()

						request.session['confer_id'] = newconfer.id

						ret["message"] = '会议创建成功，请在下方继续填写你的会议发言资料~'
						ret["status"] = "成功"
						# print("35", ret)
						del request.session['createToken']
					except:
						ret["message"] = '会议创建失败~'
						ret["status"] = "失败"
					return HttpResponse(json.dumps(ret))
			else:
				ret["message"] = '请勿重复提交~'
				return HttpResponse(json.dumps(ret))
		else:
			# err = obj.errors
			ret["message"] = confer_form.errors
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

		print(0, request.POST.dict())
		data = request.POST.getlist('dt')
		print(1, data)
		topic_num = int((len(data) - 3) / 2)
		# insert new conference
		print(topic_num)
		newtopic = models.Topic()
		sentence = {}
		for i in range(topic_num):
			# print(i,data[2*i],data[2*i+1])
			sentence[data[2 * i]] = data[2 * i + 1]
			print(sentence)
		cu_user = request.session.get('user_id')
		cu_conf = request.session.get('confer_id')
		try:
			topic = models.Topic.objects.get(people_id=cu_user, confer_id=cu_conf)
		except:
			topic = None
		if topic is not None:
			try:
				topic.sentence = sentence
				topic.share = data[-3]
				topic.pre_time = data[-2]
				topic.ex_reason = data[-1]
				topic.save()
				request.session['topic_id'] = newtopic.id
				ret["message"] = '汇报内容更新成功~'
				ret["status"] = "成功"

			except:
				ret["message"] = '汇报内容更新失败~'
		else:
			try:
				newtopic.sentence = sentence
				newtopic.share = data[-3]
				newtopic.pre_time = data[-2]
				newtopic.ex_reason = data[-1]
				newtopic.people_id = lg_models.User.objects.get(id=cu_user)
				newtopic.confer_id = models.Conference.objects.get(id=cu_conf)
				newtopic.save()
				request.session['topic_id'] = newtopic.id
				ret["message"] = '汇报内容编辑成功~'
				ret["status"] = "成功"
			except:
				ret["message"] = '汇报内容编辑失败~'

		print("35", ret)
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
	print(1, 'start')
	confer_id = request.session['confer_id']
	cu_user = request.session['user_id']
	confer = models.Conference.objects.get(id=confer_id)
	people = confer.people.all()
	people_lst = []
	for i in people:
		people_lst.append(i.name + ' / ' + i.email)
	print(confer, people_lst)
	try:
		topic = models.Topic.objects.get(confer_id=confer_id, people_id=cu_user)
		sentence = ''
		sen_dict = ast.literal_eval(topic.sentence)
		for key in sen_dict.keys():
			sentence = sentence + key + ':' + '\n' + sen_dict[key] + '\n' + '-----' * 60 + '\n'
		data = {'subcontent': sentence, 'sharecontent': topic.share, 'pretime': topic.pre_time}
		start_form = forms.StartForm(auto_id=True, data=data)
	except:
		print('topic error')
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
		# print(confer_id,people)
		try:
			topic = models.Topic.objects.get(confer_id=confer_id, people_id=people)
			sentence = ''
			sen_dict = ast.literal_eval(topic.sentence)
			for key in sen_dict.keys():
				sentence = sentence + key + ':' + '\n' + sen_dict[key] + '\n' + '-----' * 10 + '\n'
			data = {'subcontent': sentence, 'sharecontent': topic.share, 'pretime': topic.pre_time,
			        "status": '成功',
			        "message": '选择成功！'}
		except:
			topic = None
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
		# print(data)
		email = data['peop'].split('/')[1].strip()
		people = lg_models.User.objects.get(email=email)
		confer_id = request.session['confer_id']
		try:
			print(people, confer_id)
			topic = models.Topic.objects.get(confer_id=confer_id, people_id=people)
			print(data)
			sen_dict = {}
			sentence = data['sentence']
			topicsubs = sentence.split('-----' * 10)
			print(topicsubs)
			for sub in topicsubs:
				if len(sub) > 5:
					sen_lst = sub.split(':')
					sen_dict[sen_lst[0].strip()] = sen_lst[1].strip()
			topic.sentence = sen_dict
			topic.share = data['share']
			topic.real_time = data['rtime']
			if int(data['rtime']) - 60 * topic.pre_time > 0:
				topic.is_ex = True
			else:
				topic.is_ex = False
			if topic.is_ex is True:
				topic.money = (int(data['rtime']) - 60 * topic.pre_time) * 0.1
			else:
				topic.money = 0
			topic.followup = data['follup']
			topic.save()
			ret['status'] = '成功'
			ret['message'] = '保存成功'
		except Exception as err:
			topic = None
			print(format(err))
			ret['message'] = '保存失败，请联系管理员'

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

	confer_id = request.session['confer_id']
	cu_user = request.session['user_id']
	topics = models.Topic.objects.filter(confer_id=confer_id)
	conclusion = {}  # 读取topic中保存的字典并形成会议纪要的格式
	for topic in topics:
		sen_dict = ast.literal_eval(topic.sentence)
		for key in sen_dict:
			# print(key, sen_dict)
			conclusion[key] = conclusion.get(key, [])
			conclusion[key].append(
				'* [ ' + topic.people_id.name + ' ] ' + sen_dict[key].split('#')[1].replace('\n', ''))
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
	for topic in topics:
		if topic.is_ex is True:
			if topic.is_money_sub is not True:
				status = '待还'
			else:
				status = '已还'
			money = money + '* [ ' + topic.people_id.name + ' ] ' + '本次需奉献' + str(topic.money) + '元' + '，已奉献' + str(
				topic.money_sub) + '元' + '\n'
	doc = doc + '-----' * 40 + '\n' + share + '-----' * 40 + '\n' + follup + '-----' * 40 + '\n' + money + '-----' * 40 + '\n'
	confer = models.Conference.objects.get(id=confer_id)
	confer.confer_conclusion = doc
	confer.conclusioner = lg_models.User.objects.get(id=cu_user)
	confer.is_over = True
	confer.save()
	print('会议纪要保存成功')
	data = {'conferconclusion': doc}
	document_form = forms.Document(auto_id=True, data=data)
	return render(request, 'confer_manege/document.html', locals())


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
		print(data)
		conftype=models.Sysconf.objects.get(confer_type=data['cftyp'])
		confsub=data['cfsb']
		conftime=data['cftm']
		print(conftype,confsub,conftime)
		try:
			conf=models.Conference.objects.get(confer_type=conftype,subject=confsub,stime=conftime)
			conclusion=conf.confer_conclusion
			searchdata={'conclusion':conclusion,'status':'成功'}
			ret['status'] = '成功'
			return HttpResponse(json.dumps(searchdata))
		except:
			ret['massage']='抱歉，未找到相关会议'
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
