# Generated by Django 2.2.1 on 2019-07-27 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_auto_20190726_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='content_type',
        ),
        migrations.AlterField(
            model_name='comment',
            name='object_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sharing.Post', verbose_name='评论对象'),
        ),
    ]
