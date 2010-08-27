#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.location.admin import location_admin

urlpatterns = patterns('',
    (r'^admin/', include(location_admin.urls)),
)
