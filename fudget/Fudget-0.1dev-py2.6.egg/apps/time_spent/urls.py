from django.conf.urls.defaults import *

urlpatterns = patterns('time_spent', 
    url(r'^$', 'views.details', name="time-spent"),
	url(r'^(?P<month>\d{1,2})/(?P<year>\d{4})/$', 'views.details', name="time-spent"),
)