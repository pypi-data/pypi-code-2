from koe.settings import *

import os

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG=True
TEMPLATE_DEBUG=DEBUG

INSTALLED_APPS += (
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

ROOT_URLCONF = 'koe.project.development.urls'
