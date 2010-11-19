from django.conf.urls.defaults import *

from fromagerie.views import SimplePackageIndex, EnhancedPackageIndex

urlpatterns = patterns('',
   (r'^$', EnhancedPackageIndex()),
   (r'^(?P<name>[\w\.-]+)/$', 'fromagerie.views.package_overview'),
   (r'^(?P<name>[\w\.-]+)/(?P<version>[\w\.-]+)/$', 'fromagerie.views.release_overview'),
)
