from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^migrate_mail/', include('gmailcopy.migrate_mail.urls')),
    (r'^admin/', include(admin.site.urls)),
)
