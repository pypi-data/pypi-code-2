#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.measurements.admin import measurements_admin

urlpatterns = patterns('',
    (r'^admin/', include(measurements_admin.urls)),
)
