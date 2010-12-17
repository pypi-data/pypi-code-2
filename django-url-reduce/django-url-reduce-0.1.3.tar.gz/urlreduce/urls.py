from django.conf.urls.defaults import *

urlpatterns = patterns('',        
    url( r'x/([\w-]+)$', 'urlreduce.views.forward' ),
)