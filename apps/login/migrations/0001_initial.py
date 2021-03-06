# Generated by Django 2.2.1 on 2019-05-31 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('confer_manage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfirmString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=256)),
                ('c_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '确认码',
                'verbose_name_plural': '确认码',
                'ordering': ['-c_time'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('password', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('sex', models.CharField(choices=[('male', '男'), ('female', '女')], default='男', max_length=32)),
                ('role', models.CharField(choices=[('user', '普通用户'), ('admin', '管理员'), ('moneyManager', '基金管理员')], default='普通用户', max_length=32)),
                ('c_time', models.DateTimeField(auto_now_add=True)),
                ('has_confirmed', models.BooleanField(default=False)),
                ('apartment', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.ProtectedError, to='confer_manage.Apartment', verbose_name='所属部门')),
                ('phone', models.CharField(max_length=11, unique=True)),
                ('picture', models.ImageField(width_field=200,height_field=200)),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'ordering': ['-c_time'],
            },
        ),
    ]
