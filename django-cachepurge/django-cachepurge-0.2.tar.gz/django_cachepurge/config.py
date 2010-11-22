# -*- coding: utf-8 -*-
""" This module is needed by utils
"""
from django.conf import settings

USE_HTTP_1_1_PURGE = True
try:
    USE_HTTP_1_1_PURGE = settings.USE_HTTP_1_1_PURGE
except AttributeError:
    pass
