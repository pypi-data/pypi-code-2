from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.doc import documentation_view
from eyeswebapp.api.handlers import MonitorHandler, MonitorResultHandler#, DatastoreHandler

monitor_handler = Resource(MonitorHandler)
monitor_result_handler = Resource(MonitorResultHandler)
#datastore_handler = Resource(DatastoreHandler)

urlpatterns = patterns('',
    url(r'^monitor/(?P<monitor_id>\d+)/$', monitor_handler, { 'emitter_format': 'json' }),
    url(r'^monitor/$', monitor_handler, { 'emitter_format': 'json' }),

    # for processing the monitor result JSON structure and storing into data stores
    url(r'^monitor/(?P<monitor_id>\d+)/store/$', monitor_result_handler, { 'emitter_format': 'json' }),
    
    #url(r'^datastore/(?P<monitor_id>\d+)/(?P<datastore_name>\w+)$', datastore_handler, { 'emitter_format': 'json' }),
    # automatically generated documentation
    url(r'^$', documentation_view)
)