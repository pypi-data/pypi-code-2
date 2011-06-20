from django.conf.urls.defaults import *
from kforge.soleInstance import application

uriPrefix = application.dictionary[application.dictionary.words.URI_PREFIX]
if uriPrefix:
    uriPrefixPattern = uriPrefix.lstrip('/') + '/'
else:
    uriPrefixPattern = ''

urlpatterns = patterns('',
    (
        r'^%s' % uriPrefixPattern, include('kforge.django.settings.urls.kui')
    ),
)
