#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.annotation.admin import annotation_admin

urlpatterns = patterns('',
    (r'^admin/', include(annotation_admin.urls)),
)
