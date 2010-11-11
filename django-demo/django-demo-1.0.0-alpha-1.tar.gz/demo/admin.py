from demo.models import SessionDatabase
from django.conf import settings
from django.contrib import admin

# security measure, don't allow access to SessionDatabase when demo is active.
if 'demo.middleware.DemoMiddleware' not in settings.MIDDLEWARE_CLASSES:
    admin.site.register(SessionDatabase)