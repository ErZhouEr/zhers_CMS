# Generated by Django 2.2.1 on 2019-06-12 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confer_manage', '0006_conference_creatime'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='is_money_sub',
            field=models.BooleanField(default=False, verbose_name='是否全部上交'),
        ),
        migrations.AddField(
            model_name='topic',
            name='money_sub',
            field=models.FloatField(default=0.0, max_length=10, verbose_name='已交罚款金额'),
        ),
    ]
