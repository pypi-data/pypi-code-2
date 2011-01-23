# -*- coding: utf-8 -*-
#from django.db.models.signals import pre_save, pre_delete
#from django.contrib.auth.models import User
#from django.conf import settings

#from green_comments.models import Comment

#def user_pre_delete(instance, **kwargs):
    #import pdb; pdb.set_trace()
    #guest = User.objects.get(username=settings.GREEN_COMMENTS_DEFAULT_USER)
    #instance.comments.update(user=guest)

#pre_delete.connect(user_pre_delete, sender=User)
