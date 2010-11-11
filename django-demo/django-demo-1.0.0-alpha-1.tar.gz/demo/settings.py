from django.conf import settings
from datetime import timedelta

ALWAYS_IGNORE = [
    'demo',
    'sessions',
]

DB_NAME_TEMPLATE = getattr(settings, 'DEMO_DB_NAME_TEMPLATE', 'django_demo_%(num)s')
DATABASE_LIVETIME = getattr(settings, 'DEMO_DATABASE_LIVETIME', timedelta(days=1))
FIXTURES = getattr(settings, 'DEMO_FIXTURES', [])
IGNORES = getattr(settings, 'DEMO_IGNORE_APPS', [])
MAX_DATABASES = getattr(settings, 'DEMO_MAX_DATABASES', 0)
BACKEND = getattr(settings, 'DEMO_BACKEND', None)
ALLOW_SHARE = getattr(settings, 'DEMO_ALLOW_SHARE', True)
SHARE_PARAMETER = getattr(settings, 'DEMO_SHARE_PARAMETER', 'share')

for required in ALWAYS_IGNORE:
    if not required in IGNORES:
        IGNORES.append(required)