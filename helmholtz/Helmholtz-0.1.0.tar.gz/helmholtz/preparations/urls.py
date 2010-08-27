#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.preparations.admin import preparations_admin

urlpatterns = patterns('',
    (r'^admin/', include(preparations_admin.urls)),
)
