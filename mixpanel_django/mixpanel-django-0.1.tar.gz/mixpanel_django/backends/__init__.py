#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import parse_backend_uri
from django.utils import importlib
from django.core import cache

BACKEND = {
    'dummy': 'dummy',
    'direct': 'direct',
    'beanstalk': 'beanstalk'
}

def _get_backend(backend_uri):
    scheme, host, params = parse_backend_uri(backend_uri)
    if scheme in BACKEND:
        name = 'mixpanel_django.backends.%s' % BACKEND[scheme]
    else:
        name = scheme
    module = importlib.import_module(name)
    return getattr(module, 'MixpanelBackend', None)(host, params)

mp_backend = _get_backend(getattr(settings, 'MP_BACKEND', 'dummy://'))


