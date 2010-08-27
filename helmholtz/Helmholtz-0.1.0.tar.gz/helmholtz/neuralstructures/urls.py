#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.neuralstructures.admin import neuralstructures_admin

urlpatterns = patterns('',
    (r'^admin/', include(neuralstructures_admin.urls)),
)
