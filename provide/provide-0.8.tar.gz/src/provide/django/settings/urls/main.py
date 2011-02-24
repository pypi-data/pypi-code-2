from django.conf.urls.defaults import *
from provide.soleInstance import application
from provide.dictionarywords import URI_PREFIX

uriPrefix = application.dictionary[URI_PREFIX]

if uriPrefix:
    uriPrefix = uriPrefix.lstrip('/')
    uriPrefix = uriPrefix + '/'

urlpatterns = patterns('',
    (
        r'^%s' % uriPrefix, include('provide.django.settings.urls.eui')
    ),
)

