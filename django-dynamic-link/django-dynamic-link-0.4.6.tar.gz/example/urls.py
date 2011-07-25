from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from dynamicLink import dl_settings

urlpatterns = patterns('',
    # Example:
    (r'^$', direct_to_template, {'template': 'home.html'}),


    # for django-dynamic-link. By default it catch url/serve/some-dynamic-link/
    (r'^\w+/%s/' % dl_settings.DOWNLINK_SERVE_PATH, include('dynamicLink.urls')), 

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
