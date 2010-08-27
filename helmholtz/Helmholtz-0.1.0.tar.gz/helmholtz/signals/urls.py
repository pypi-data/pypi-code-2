#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.signals.admin import signals_admin

urlpatterns = patterns('',
    (r'^admin/', include(signals_admin.urls)),
) 
