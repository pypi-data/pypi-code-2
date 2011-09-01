from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^frontwebproject/', include('frontwebproject.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    # Descomentar y comentar la anterior para deshabilitar todos los plugins:
    # ("^(.*)$", 'frontweb.views.query_file'),

    (r'', include("frontweb.urls"),),
)
