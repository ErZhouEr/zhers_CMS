from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.contrib import messages

import json
from datetime import datetime

from . import models
from . import forms
from apps.login import models as lg_models

from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def dashboard(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	return render(request, 'confer_manege/dashboard.html', locals())


def usertask(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	return render(request, 'confer_manege/usertask.html',locals())

# def dropconfer(request):
# 	if not request.session.get('is_login', None):
# 		return redirect('/login/')
# 	return render(request,'confer_manege/edit.html')


def create(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	conftype = request.GET.get('confertype')
	conferstartime=request.GET.get('startime')
	conferstartime=str(conferstartime).replace('000','')
	formated_stime=datetime.fromtimestamp(float(conferstartime))
	conferendtime = request.GET.get('endtime')
	# print(conftype,conferstartime,conferendtime)
	users = lg_models.User.objects.filter(has_confirmed=1)
	cu_user=request.session['user_id']
	# 在服务端session中添加key认证，避免用户重复提交表单
	token = '10000'  # 可以采用随机数
	request.session['createToken'] = token

	request.session['conftype']=conftype
	# request.session['formated_stime'] = formated_stime

	# if request.method == 'POST':
	# 	confer_form = forms.ConferForm(request.POST)
	# 	message = "请检查填写的内容！"
	# 	print(confer_form)
	# 	ret = {"status": None, "message": None}
	# 	if confer_form.is_valid():
	# 		# client_token = request.POST.get('createtoken')
	# 		# server_token = request.session['createToken']
	# 		# print(client_token,server_token)
	# 		confertype = conftype
	# 		confersub=confer_form.cleaned_data.get('confersub')
	# 		conferproj = confer_form.cleaned_data.get('conferproj')
	# 		conferpeople=confer_form.cleaned_data.get('people')
	# 		confertime=confer_form.cleaned_data.get('stime')
	# 		peoplelst=conferpeople.split(',')
	# 		startime,endtime=confertime.split('-')
	# 		if len(peoplelst)<2:
	# 			message='会议人数太少，请继续添加~'
	# 			edit_Form = forms.EditForm(auto_id=True)
	# 			return render(request, 'confer_manege/edit.html', locals())
	# 		#elif int(endtime)-int(startime)<0:   #还要判断日期大于当前日期
	# 		#	message='会议时间有误，请再检查下~'
	# 			# return render(request, 'confer_manege/edit.html', locals())
	# 		cf_type=models.Sysconf.objects.get(confer_type=confertype)
	# 		cf_proj=models.Project.objects.get(projname=conferproj)
	# 		newconfer=models.Conference()
	# 		newconfer.confer_type=cf_type
	# 		newconfer.confer_proj=cf_proj
	# 		newconfer.subject=confersub
	# 		#newconfer.people=peoplelst
	# 		newconfer.stime=formated_stime
	# 		newconfer.save()
	#
	# 		request.session['confer_id']=newconfer.id
	#
	# 		message='会议创建成功，请在下方继续填写你的会议发言资料~'
	# 		messages.success(request, '会议创建成功，请在下方继续填写你的会议发言资料~')
	# 		print(message)
	# 		edit_Form = forms.EditForm(auto_id=True)
	# 		return render(request,'confer_manege/edit.html', locals())
	# 	else:
	# 		print(0)
	# 		print(confer_form.errors)
	# 		edit_Form = forms.EditForm(auto_id=True)
	# 		return render(request, 'confer_manege/edit.html', locals())

	confer_form = forms.ConferForm(auto_id=True)
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
			print("31----", confer_form.cleaned_data)
			#防止重复提交
			client_token = request.POST.get('createtoken')
			server_token = request.session.get('createToken',None)
			print(client_token,server_token,client_token==server_token)
			if client_token==server_token:
				#insert new conference
				cu_user = request.session.get('user_id', None)
				confertype = request.session.get('conftype',None)
				confersub = confer_form.cleaned_data.get('confersub')
				conferproj = confer_form.cleaned_data.get('conferproj')
				conferpeople = confer_form.cleaned_data.get('people')
				confertime = confer_form.cleaned_data.get('stime')
				peoplelst = conferpeople.split(',')
				startime, endtime = confertime.split('-')
				if len(peoplelst) < 2:
					ret["message"] = '会议人数太少，请继续添加~'
					return HttpResponse(json.dumps(ret))
				# elif int(endtime)-int(startime)<0:   #还要判断日期大于当前日期
				#	message='会议时间有误，请再检查下~'
				# return render(request, 'confer_manege/edit.html', locals())
				cf_type = models.Sysconf.objects.get(confer_type=confertype)
				cf_proj = models.Project.objects.get(projname=conferproj)
				cf_creater=lg_models.User.objects.get(id=cu_user)
				print(cu_user)
				newconfer = models.Conference()
				newconfer.confer_type = cf_type
				newconfer.confer_proj = cf_proj
				newconfer.subject = confersub
				newconfer.creater=cf_creater
				# newconfer.people=peoplelst
				# newconfer.stime = request.session.get('formated_stime',None)
				newconfer.save()

				request.session['confer_id'] = newconfer.id

				ret["message"] = '会议创建成功，请在下方继续填写你的会议发言资料~'
				ret["status"] = "成功"
				print("35", ret)
				del request.session['createToken']
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
		print(1,request.POST)
		edit_form = forms.EditForm(request.POST)
		ret = {"status": None, "message": None}

		if edit_form.is_valid():
			print("31----", edit_form.cleaned_data)

				#insert new conference

			ret["message"] = '汇报内容编辑成功~'
			ret["status"] = "成功"
			print("35", ret)
			del request.session['createToken']
			return HttpResponse(json.dumps(ret))

		else:
			ret["message"] = '输入不合理，请检查输入~'
			return HttpResponse(json.dumps(ret))


def edit(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	if request.method == 'POST':
		edit_Form = forms.EditForm(request.POST)
		message = "请检查填写的内容！"
		if edit_Form.is_valid():
			subjectname=edit_Form.cleaned_data.get('subjectname')
			subcontent=edit_Form.cleaned_data.get('subcontent')
			pretime=edit_Form.cleaned_data.get('pretime')
			exreason=edit_Form.cleaned_data.get('exreason')

			newtopic=models.Topic()
			newtopic.sentence=str({'subject':subjectname,'content':subcontent})
			newtopic.pre_time=pretime
			newtopic.ex_reason=exreason
			newtopic.people_id=request.session.get('user_id')
			newtopic.confer_id=request.session.get('confer_id')

			newtopic.save()

			request.session['topic_id'] = newtopic.id

			return render(request,'confer_manege/edit.html', locals())
		else:
			return render(request, 'confer_manege/edit.html', locals())
	edit_Form = forms.EditForm(auto_id=True)
	confer_form = forms.ConferForm(auto_id=True)
	return render(request, 'confer_manege/edit.html', locals())


def start(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	if request.method == 'POST':
		start_form = forms.StartForm(request.POST)
		message = "请检查填写的内容！"
		if start_form.is_valid():
			return render(request,'confer_manege/start.html', locals())
		else:
			return render(request, 'confer_manege/start.html', locals())
	start_form = forms.StartForm(auto_id=True)
	return render(request, 'confer_manege/start.html', locals())

def document(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	if request.method == 'POST':
		document_form = forms.Document(request.POST)
		message = "请检查填写的内容！"
		if document_form.is_valid():
			return render(request,'confer_manege/document.html', locals())
		else:
			return render(request, 'confer_manege/document.html', locals())
	document_form = forms.Document(auto_id=True)
	return render(request, 'confer_manege/document.html', locals())

#---------------------数据库与前端页面交互生成前端元素---------------------------
Confer_dict = {
	"普通小型会议": {
		"啊啊啊啊": ["哈哈", "嘎嘎"],
		"噢噢噢噢": ["问问", "嗯嗯", "然然"],
		"呜呜呜呜": ["刚刚", "等等", "找找"]
	},
	"项目例会": {
		"练练": ["12", "23", "34"],
		"吉吉": []
	},
	"部门例会": {
		"45": [],
		"67": []
	}
};


def getSubData(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	confertype = request.GET['confertype']
	Sub_list = []
	for sub in Confer_dict[confertype]:
		Sub_list.append(sub)
	return HttpResponse(json.dumps(Sub_list))


def getTimeData(request):
	if not request.session.get('is_login', None):
		return redirect('/login/')
	confertype, confersub = request.GET['confertype'], request.GET['confersub']
	Time_list = Confer_dict[confertype][confersub]
	return HttpResponse(json.dumps(Time_list))

