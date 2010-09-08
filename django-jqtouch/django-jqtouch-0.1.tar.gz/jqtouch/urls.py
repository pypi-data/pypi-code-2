from django.conf import settings
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns('jqtouch.views',
    url('^$', 'base', name='jqtouch-base',
        kwargs={'identifier':settings.JQTOUCH_BASE_IDENTIFIER}),
    url('^(?P<identifier>[\w\-_]{1,64})/$', 'base',
        name='jqtouch-ajax-panel'),
)
