# Generated by Django 2.2.1 on 2019-06-03 21:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_confirmstring_user'),
        ('confer_manage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='无主题', max_length=50, verbose_name='会议主题')),
                ('process', models.FloatField(default=0.0, max_length=10, verbose_name='会议进展')),
                ('stime', models.CharField(default='', max_length=30, verbose_name='开始时间')),
                ('time', models.FloatField(default=0.0, max_length=10, verbose_name='持续时间')),
                ('ex_time', models.IntegerField(default=0, verbose_name='超时时间')),
                ('confer_conclusion', models.TextField(default='', max_length=1500, verbose_name='会议纪要')),
                ('is_over', models.BooleanField(default=False, verbose_name='是否完成')),
                ('conclusioner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.ProtectedError, related_name='conclusion_people', to='login.User', verbose_name='会议记录人')),
                ('confer_apart', models.ForeignKey(null=True, on_delete=django.db.models.deletion.ProtectedError, to='confer_manage.Apartment', verbose_name='所属部门')),
                ('confer_proj', models.ForeignKey(default=-1, null=True, on_delete=django.db.models.deletion.ProtectedError, to='confer_manage.Project', verbose_name='所属项目')),
                ('confer_type', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.ProtectedError, to='confer_manage.Sysconf', verbose_name='会议类型')),
                ('creater', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.ProtectedError, related_name='conference_creater', to='login.User', verbose_name='创建人员')),
                ('people', models.ManyToManyField(default='', to='login.User', verbose_name='参会人员')),
                ('is_start', models.BooleanField(default=False, verbose_name='是否已经开始')),
            ],
            options={
                'verbose_name': '会议',
                'verbose_name_plural': '会议',
                'ordering': ['-stime'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence', models.TextField(max_length=200, verbose_name='汇报内容')),
                ('share', models.TextField(default='', max_length=200, verbose_name='分享内容')),
                ('pre_time', models.FloatField(default=0.0, max_length=10, verbose_name='预计时长')),
                ('real_time', models.IntegerField(default=0, verbose_name='真实时长')),
                ('is_ex', models.BooleanField(default=False, verbose_name='是否超时')),
                ('ex_reason', models.CharField(max_length=30, verbose_name='超时原因')),
                ('ex_time', models.IntegerField(default=0, verbose_name='超时时间')),
                ('followup', models.CharField(default='', max_length=50, verbose_name='跟踪问题')),
                ('money', models.FloatField(default=0.0, max_length=10, verbose_name='罚款金额')),
                ('confer_id', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.ProtectedError, to='confer_manage.Conference', verbose_name='会议id')),
                ('people_id', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.ProtectedError, to='login.User', verbose_name='汇报人id')),
            ],
            options={
                'verbose_name': '汇报内容',
                'verbose_name_plural': '汇报内容',
            },
        ),
    ]
