"""
URL test patterns for panorama. Use this file to ensure a consistent
set of URL patterns are used when running unit tests. This test_urls
module should be referred to by your test class.
"""

from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('panorama.views',
  (r'^panoramas/', include('panorama.urls')),
)
