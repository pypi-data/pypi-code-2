#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.units.admin import units_admin

urlpatterns = patterns('',
    (r'^admin/', include(units_admin.urls)),
)
