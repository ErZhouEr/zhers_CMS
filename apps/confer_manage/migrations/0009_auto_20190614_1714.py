# Generated by Django 2.2.1 on 2019-06-14 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('confer_manage', '0008_auto_20190614_1646'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fund',
            old_name='confer_apart',
            new_name='fund_apart',
        ),
    ]
