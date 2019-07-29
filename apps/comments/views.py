from django.shortcuts import render,reverse,redirect
from .models import Comment
from .forms import CommentForm
from apps.login import models as lg_models
from apps.sharing.models import Post
from notifications.signals import notify
from django.utils.html import strip_tags

# 添加评论
def update_comment(request, post_pk):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    referer = request.META.get('HTTP_REFERER', reverse('sharing:index'))
    comment_form = CommentForm(request.POST)
    cu_user = request.session['user_id']
    user = lg_models.User.objects.get(id=cu_user)
    post=Post.objects.get(id=post_pk)
    # print(request.POST,'------------\n')
    # print(comment_form,'------------\n')

    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = Comment()
        comment.user = user
        comment.text = comment_form.cleaned_data['text']
        comment.object_id = post
        # print(2, comment,'------------\n')

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()
    else:
        print(comment_form.errors,'------------\n')

    return redirect(referer+'#comment')