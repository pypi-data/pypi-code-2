#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('mp_example',
    # Example:
    (r'^$', 'views.test_mp_view'),
)