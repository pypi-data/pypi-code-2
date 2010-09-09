from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<shortname>\w+)', 'shorturls.views.index'),
)
