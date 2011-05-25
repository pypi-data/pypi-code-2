from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
import django.contrib.auth.urls
import desktopnotifications.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^notifications/', include(desktopnotifications.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(django.contrib.auth.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)