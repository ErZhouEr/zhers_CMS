from django.db import models
# from django.contrib.auth.models import User

# Create your models here.

class User(models.Model):

    gender = (
        ('male', "男"),
        ('female', "女"),
    )

    roles = (
        ('user', '普通用户'),
        ('admin', "管理员"),
        ('moneyManager',"基金管理员")
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    phone=models.CharField(max_length=11,unique=True)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    role = models.CharField(max_length=32, choices=roles, default="普通用户")
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)
    apartment = models.ForeignKey('confer_manage.Apartment', on_delete=models.ProtectedError, verbose_name='所属部门', default=-1)
    picture=models.ImageField(upload_to='image',width_field='width',height_field='height',default='image/avatar.png')
    width=models.IntegerField(default=200)
    height = models.IntegerField(default=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE,default=-1)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:

        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"