# Generated by Django 2.2.1 on 2019-07-02 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_auto_20190701_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='picture',
            field=models.ImageField(height_field='200px', upload_to='../static/login/image/', width_field='200px'),
        ),
    ]
