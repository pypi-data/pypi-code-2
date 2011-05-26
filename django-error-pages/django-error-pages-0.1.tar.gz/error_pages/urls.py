from django.conf.urls.defaults import patterns, url

_PREFIX = '__errorpage__'

urlpatterns = patterns('error_pages.views',
    url(r'^%s/$' % _PREFIX, 'display_error')
)
