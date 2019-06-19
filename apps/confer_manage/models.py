from django.db import models
from datetime import datetime



# Create your models here.


class Project(models.Model):
	projname = models.TextField(max_length=20, verbose_name='项目名称')

	def __str__(self):
		return self.projname

	class Meta:
		verbose_name = "项目名称"
		verbose_name_plural = "项目名称"


class Apartment(models.Model):
	apartment = models.TextField(max_length=20, verbose_name='部门名称')

	def __str__(self):
		return self.apartment

	class Meta:
		verbose_name = "部门名称"
		verbose_name_plural = "部门名称"


class Sysconf(models.Model):
	confer_type = models.CharField(max_length=30, verbose_name='会议类型')

	def __str__(self):
		return self.confer_type

	class Meta:
		verbose_name = "系统默认项"
		verbose_name_plural = "系统默认项"


class Conference(models.Model):
	confer_type = models.ForeignKey(Sysconf, on_delete=models.ProtectedError, verbose_name='会议类型',default=-1)
	confer_proj=models.ForeignKey(Project, on_delete=models.ProtectedError, verbose_name='所属项目',default=-1,null=True)
	confer_apart = models.ManyToManyField(Apartment, verbose_name='所属部门',default='')
	subject = models.CharField(max_length=50, verbose_name='会议主题',default='无主题')
	process = models.FloatField(max_length=10, verbose_name='会议进展',default=0.0)   #实际输出百分比形式
	creatime = models.CharField(verbose_name='创建时间', max_length=30, default='')
	stime = models.CharField(verbose_name='开始时间',max_length=30,default='')
	endtime = models.CharField(max_length=30, verbose_name='结束时间',default='')
	# ex_time = models.IntegerField(verbose_name='超时时间',default=0)  #单位为秒
	creater = models.ForeignKey(to='login.User', related_name='conference_creater',on_delete=models.ProtectedError,verbose_name='创建人员', default=-1)
	people = models.ManyToManyField(to='login.User', verbose_name='参会人员',default='')
	confer_conclusion = models.TextField(max_length=1500, verbose_name='会议纪要',default='')
	conclusioner=models.ForeignKey(to='login.User',related_name='conclusion_people',on_delete=models.ProtectedError,verbose_name='会议记录人',null=True)
	# is_start=models.CharField(default=False, verbose_name='是否已经开始')
	is_over=models.BooleanField(default=False, verbose_name='是否完成')


	def __str__(self):
		return self.subject

	class Meta:
		ordering = ["-stime"]
		verbose_name = "会议"
		verbose_name_plural = "会议"


class Topic(models.Model):
	sentence = models.TextField(max_length=200, verbose_name='汇报内容')
	share=models.TextField(max_length=200, verbose_name='分享内容',default='')
	confer_id = models.ForeignKey(Conference, on_delete=models.ProtectedError, verbose_name='会议id',default=-1)
	pre_time = models.FloatField(max_length=10, verbose_name='预计时长',default=0.0)
	is_prepared=models.BooleanField(default=False, verbose_name='是否主动提交摘要')
	real_time = models.IntegerField(verbose_name='真实时长',default=0)  #单位为秒
	is_ex = models.BooleanField(default=False, verbose_name='是否超时')
	ex_reason = models.CharField(max_length=30, verbose_name='超时原因')
	ex_time = models.IntegerField(verbose_name='超时时间',default=0)
	people_id = models.ForeignKey(to='login.User', on_delete=models.ProtectedError, verbose_name='汇报人id',default=-1)
	followup = models.CharField(max_length=50, verbose_name='跟踪问题',default='')
	money = models.FloatField(max_length=10, verbose_name='罚款金额',default=0.0)
	money_sub = models.FloatField(max_length=10, verbose_name='已交罚款金额', default=0.0)
	is_money_sub=models.BooleanField(default=False, verbose_name='是否全部上交')

	def __str__(self):
		return self.sentence

	class Meta:
		verbose_name = "汇报内容"
		verbose_name_plural = "汇报内容"


class Fund(models.Model):
	fund_apart = models.ForeignKey(Apartment,on_delete=models.ProtectedError, verbose_name='所属部门', default='')
	reason=models.TextField(max_length=200, verbose_name='收入事由',default='')
	money = models.FloatField(max_length=10, verbose_name='收入金额',default=0.0)
	income_confer = models.ForeignKey(Conference,on_delete=models.ProtectedError, verbose_name='收入所属会议', default='')
	income_people=models.ForeignKey(to='login.User', on_delete=models.ProtectedError,verbose_name='创建人员', default='')
	money_sub = models.FloatField(max_length=10, verbose_name='已交罚款金额', default=0.0)
	is_money_sub = models.BooleanField(default=False, verbose_name='是否全部上交')


	def __str__(self):
		return self.reason+str(self.money)

	class Meta:
		verbose_name = "基金情况"
		verbose_name_plural = "基金情况"