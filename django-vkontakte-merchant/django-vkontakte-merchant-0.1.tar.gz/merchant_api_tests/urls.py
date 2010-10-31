from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^merchant/', include('merchant_api.urls')),
)
