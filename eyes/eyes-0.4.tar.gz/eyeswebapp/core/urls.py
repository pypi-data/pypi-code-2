# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('core.views',
    (r'^$', 'index'),
    (r'^monitor/(\d+)/$', 'monitor_detail'), #, name='monitor_detail'
    (r'^host/(\d+)/$', 'host_detail'), #, name='host_detail'
    (r'^datastore/(\d+)/$', 'datastore_detail'), #, name='datastore_detail'
    (r'^datastore/(\d+)/png$', 'datastore_image'), #, name='datastore_image'
    (r'^visualtest/$', 'visual_test'),
)
