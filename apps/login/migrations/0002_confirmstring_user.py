# Generated by Django 2.2.1 on 2019-05-31 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmstring',
            name='user',
            field=models.OneToOneField(default=-1, on_delete=django.db.models.deletion.CASCADE, to='login.User'),
        ),
    ]
