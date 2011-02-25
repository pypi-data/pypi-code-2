import os

from django.conf import settings

# Project default domain name
HOST_DOMAIN = getattr(settings, 'HOST_DOMAIN', 'example.com')

# Default backend host
BACKEND_PORT = getattr(settings, 'BACKEND_PORT', '8080')

# Project home directory
PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT', '/var/www/')

# WSGI configuration
WSGI_FILE_PATH = os.path.join(PROJECT_ROOT, 'apache.wsgi')
WSGI_USER = getattr(settings, 'WSGI_USER', 'user')
WSGI_GROUP = getattr(settings, 'WSGI_GROUP', 'group')
WSGI_PATH = getattr(settings, 'WSGI_PATH', PROJECT_ROOT)
