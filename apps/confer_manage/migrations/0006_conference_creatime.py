# Generated by Django 2.2.1 on 2019-06-11 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confer_manage', '0005_remove_conference_ex_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='creatime',
            field=models.CharField(default='', max_length=30, verbose_name='创建时间'),
        ),
    ]
