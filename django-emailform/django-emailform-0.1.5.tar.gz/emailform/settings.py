import re

from django.conf import settings as _gs


EMAILFORM_EMAIL_FROM = getattr(_gs,
                            'EMAILFORM_EMAIL_FROM',
                            'donotreply@donotreply.com')


EMAILFORM_ADMIN_SITE = getattr(_gs, 'EMAILFORM_ADMIN_SITE', '')
