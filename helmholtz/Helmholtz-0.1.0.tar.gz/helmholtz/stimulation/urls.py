#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.stimulation.admin import stimulation_admin

urlpatterns = patterns('',
    (r'^admin/', include(stimulation_admin.urls)),
) 
