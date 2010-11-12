from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

alawys_ignore = [
    'demo',
    'sessions',
]
package, name = getattr(
    settings,
    'DEMO_FILE_STORAGE',
    'django.core.files.storage.FileSystemStorage'
).rsplit('.',1)


DB_NAME_TEMPLATE = getattr(settings, 'DEMO_DB_NAME_TEMPLATE', 'django_demo_%(num)s')
DATABASE_LIVETIME = getattr(settings, 'DEMO_DATABASE_LIVETIME', timedelta(days=1))
FIXTURES = getattr(settings, 'DEMO_FIXTURES', [])
IGNORES = getattr(settings, 'DEMO_IGNORE_APPS', [])
MAX_DATABASES = getattr(settings, 'DEMO_MAX_DATABASES', 0)
BACKEND = getattr(settings, 'DEMO_BACKEND', None)
ALLOW_SHARE = getattr(settings, 'DEMO_ALLOW_SHARE', True)
SHARE_PARAMETER = getattr(settings, 'DEMO_SHARE_PARAMETER', 'sharedemo')
FILE_STORAGE = getattr(import_module(package), name)
CELERY = getattr(settings, 'DEMO_USE_CELERY', False)
if CELERY and 'celery' not in settings.INSTALLED_APPS: # pragma: no cover
    raise ImproperlyConfigured("django-demo cannot use celery if it's not installed")

# never read 'demo' or 'session' from client databases
for required in alawys_ignore:
    if not required in IGNORES: # pragma: no cover
        IGNORES.append(required)