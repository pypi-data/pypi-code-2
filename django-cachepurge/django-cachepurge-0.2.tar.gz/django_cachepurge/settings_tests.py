# -*- coding: utf-8 -*-
""" Settings for running tests
"""
DATABASE_ENGINE = 'sqlite3'

ROOT_URLCONF = ''

CACHE_URLS = 'http://127.0.0.1:3128'

INSTALLED_APPS = (
    'django_cachepurge',
    )

MIDDLEWARE_CLASSES = (
    #'django.middleware.common.CommonMiddleware',
    'django_cachepurge.middleware.CachePurge',
    )
