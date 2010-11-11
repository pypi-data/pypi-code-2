from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('genericforeignkey.views',
    url(r'^generic_object_list/$', 'generic_object_list', name='generic_object_list'),
)
