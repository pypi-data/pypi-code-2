import os
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', include('homepage.urls')),
	(r'^time-spent/', include('time_spent.urls')),
	(r'^accounts/', include('registration.urls')),

    # Example:
    # (r'^Fudget/', include('Fudget.foo.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
		'document_root': os.path.join(settings.PROJECT_ROOT, "media"),
		'show_indexes': True,
		}),
	)