# -*- coding: utf-8 -*-

from os.path import join, dirname

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponse, HttpResponseServerError
from django.template.context import RequestContext, Context

# Handle critical errors

def error500(request, template_name='500.html'):
    try:
        output = render_to_string(template_name, {}, RequestContext(request))
    except:
        output = "Critical error. Administrator was notified."
    return HttpResponseServerError(output)
handler500 = 'harness.urls.error500'

# Connect admin

admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
) 

# Define debug-mode URLs

# static urls will be disabled in production mode,
# forcing user to configure httpd
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(.*)$',
            'django.views.static.serve',
            dict(document_root=settings.MEDIA_ROOT)
        ),
        url(r'^static/(.*)$',
            'django.views.static.serve',
            dict(document_root=settings.STATIC_ROOT)
        ),
        url(r'^admin-media/(.*)$',
            'django.views.static.serve',
            dict(document_root=join(dirname(admin.__file__), 'media'))
        ),
    )
