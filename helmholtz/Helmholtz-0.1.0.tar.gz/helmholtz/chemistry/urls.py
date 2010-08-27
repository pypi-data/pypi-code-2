#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.chemistry.admin import chemistry_admin

urlpatterns = patterns('',
    (r'^admin/', include(chemistry_admin.urls)),
)
