from django.conf import settings
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import include

from koe.urls import urlpatterns

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': settings.SITE_ROOT + '/static/'
    , 'show_indexes': True}),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': settings.SITE_ROOT + '/uploads/'
    , 'show_indexes': True}),
    #(r'^init/', include('myproject.urls')),
) + urlpatterns
