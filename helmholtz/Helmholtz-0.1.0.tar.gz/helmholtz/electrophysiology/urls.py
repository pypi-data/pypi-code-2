#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.electrophysiology.admin import electrophysiology_admin

urlpatterns = patterns('',
    (r'^admin/', include(electrophysiology_admin.urls)),
)
