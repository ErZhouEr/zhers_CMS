from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = 'apps.comments'

    def ready(self):                           #这是什么原理，为啥import了signals就有用了
        super(CommentsConfig,self).ready()
        # from . import signals
