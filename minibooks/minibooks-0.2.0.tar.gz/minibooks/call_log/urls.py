from django.conf.urls.defaults import *
from call_log.views import *

urlpatterns = patterns('',
    (r'^call_log/$', log),
)
