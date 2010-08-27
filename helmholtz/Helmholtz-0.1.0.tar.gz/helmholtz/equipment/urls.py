#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.equipment.admin import equipment_admin

urlpatterns = patterns('',
    (r'^admin/', include(equipment_admin.urls)),
)
