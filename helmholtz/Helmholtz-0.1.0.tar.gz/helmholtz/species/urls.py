#encoding:utf-8
from django.conf.urls.defaults import patterns, include
from helmholtz.species.admin import species_admin

urlpatterns = patterns('',
    (r'^admin/', include(species_admin.urls)),
) 
