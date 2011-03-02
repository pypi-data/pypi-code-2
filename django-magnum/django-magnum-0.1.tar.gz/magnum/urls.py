from django.conf.urls.defaults import *


urlpatterns = patterns('magnum.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<package_name>(?!favicon\.ico/?$)[^/]+)/$', 'package', name='package'),
    url(r'^(?P<package_name>[^/]+)/(?P<filename>[^/]+)$', 'download_dist', name='download_dist')
)
