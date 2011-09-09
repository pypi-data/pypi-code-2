#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

import urllib
from random import choice
import logging
from copy import copy

# Request URL:
# Type
# Country code
# Anonymity level
# Max conn time
# Min speed
# Last check

BASE_URL = 'http://worldofproxy.com/getx%s.html'

# Types of proxy
HTTP = 0
SSL = 1
HTTP_SSL = 2
SOCKS4 = 3
SOCKS5 = 4

ANY_TYPE = 0
TRANSPARENT_TYPE = 1
ANONYMOUS_TYPE = 2
ELITE_TYPE = 3

CACHE = []

def load_list(key, conn=HTTP, type=ANONYMOUS_TYPE, country='', max_conn='', min_speed='', last_check=''):
    params = '_%s_%s_%s_%s_%s_%s_%s' % (key, conn, country, type, max_conn, min_speed, last_check)
    logging.debug('loading proxy list %s' % params)
    url = BASE_URL % params
    data = urllib.urlopen(url).read()
    CACHE.extend(data.splitlines())
    logging.debug('loaded %s proxies' % len(CACHE))
    return copy(CACHE)

def random_proxy(key=None, **kwargs):
    if CACHE:
        return choice(CACHE)
    elif key:
        load_list(key, **kwargs)
        return choice(CACHE)
    else:
        raise ValueError('You should call load_list before or provide key argument')