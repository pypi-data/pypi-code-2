#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from . import views


urlpatterns = patterns('',
    url(r"^message-tester/$", views.generate_identity),
    url(r"^message-tester/(?P<identity>\d+)/$", views.message_tester))
