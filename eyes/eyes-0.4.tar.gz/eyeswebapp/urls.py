from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'frontpage.html'}),
    (r'^core/', include('eyeswebapp.core.urls')),
    (r'^api/', include('eyeswebapp.api.urls')),
    
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    ## Override the default registration form
    #url(r'^account/register/$', 'registration.views.register',
    #    kwargs={'form_class': UserRegistrationForm},
    #    name='registration_register'),
)

# Add static media if running in DEBUG mode
if settings.DEBUG: # pragma: no cover
    urlpatterns += patterns('django.views.static',
        (r'^static_media/(?P<path>.*)$', 'serve', {
            'show_indexes': True,
            'document_root': settings.MEDIA_ROOT,
            }),
    )
