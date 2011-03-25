import re

from django.conf import settings as _gs


EMAILFORM_EMAIL_FROM = getattr(_gs, 'EMAILFORM_EMAIL_FROM', None)
if EMAILFORM_EMAIL_FROM is None:
    EMAILFORM_EMAIL_FROM = getattr(_gs, 'DEFAULT_FROM_EMAIL', None)
if EMAILFORM_EMAIL_FROM is None:
    EMAILFORM_EMAIL_FROM = 'donotreply@donotreply.com'


EMAILFORM_ADMIN_SITE = getattr(_gs, 'EMAILFORM_ADMIN_SITE', '')
