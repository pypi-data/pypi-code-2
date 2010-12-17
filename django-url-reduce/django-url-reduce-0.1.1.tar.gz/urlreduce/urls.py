from django.conf.urls.defaults import *

urlpatterns = patterns('',        
    url( r'([\w-]+)$', 'urlreduce.views.forward' ),
)