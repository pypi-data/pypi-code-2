#:coding=utf-8:

from django.http import get_host
from django.conf import settings as django_settings
from beproud.django.ssl.conf import settings

__all__ = ('conf',)

def conf(request):
    return {
        'USE_SSL': settings.USE_SSL,
        'HTTP_HOST': getattr(django_settings, 'HTTP_HOST', get_host(request)),
        'SSL_HOST': getattr(django_settings, 'SSL_HOST', get_host(request)),
    }
