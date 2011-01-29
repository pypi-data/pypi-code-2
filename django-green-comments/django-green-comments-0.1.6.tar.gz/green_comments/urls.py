# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('green_comments.views',
    url(r'^create/(\d+)/(\d+)/$', 'comment_create', name='comment_create'),
    url(r'^comment/(\d+)/reply/$', 'comment_reply', name='comment_reply'),
)
