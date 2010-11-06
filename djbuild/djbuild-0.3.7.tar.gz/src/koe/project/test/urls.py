from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import include

from 'koe.urls import urlpatterns

urlpatterns = patterns('',
    #(r'^init/', include('myproject.urls')),
) + urlpatterns
