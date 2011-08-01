from django.conf.urls.defaults import *
from django.conf import settings
import views

urlpatterns = patterns('',
	('^(?P<model>\w+)/(?P<function>\w+)', views.json_api)
)

if settings.DEBUG:
	urlpatterns += patterns('',('docs', views.docs))
