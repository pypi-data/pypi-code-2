#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.storage.admin import storage_admin

urlpatterns = patterns('',
    (r'^admin/', include(storage_admin.urls)),
) 
