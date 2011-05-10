from django.conf.urls.defaults import *

from evo.settings import STATIC_ROOT

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    #(r'^evo/', include('evo.web.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^$', 'evo.web.views.index'),
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': STATIC_ROOT}),
)



