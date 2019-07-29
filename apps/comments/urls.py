from django.conf.urls import url

from . import views
from django.urls import path

app_name = 'comments'
urlpatterns = [
    path('comment/post/<int:post_pk>/', views.update_comment, name='update_comment'),
]
