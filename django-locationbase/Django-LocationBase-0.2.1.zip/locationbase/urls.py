from django.conf.urls.defaults import *

from locationbase.views import *

urlpatterns = patterns('',
    url(r'^fromgeocoding/$', location_from_geocoding, name='location_from_geocoding'),
    url(r'^geocoding/$', geocoding, name='geocoding'),
)