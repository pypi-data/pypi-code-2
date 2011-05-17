"""
Interface to http://worldofproxy.com site. The site which provides proxy lists.
To work with this module you have to:

1) Create settings.py with following content:

    WORLDOFPROXY_KEY = "...your key..."

2) Create directory "var" where list of proxy will be cached for 10 minutes

3) Enjoy:

    >>> from tools.proxy.worldofproxy import random_proxy
    >>> random_proxy()
    ('174.52.83.46:1635', 'socks5')

To get one random proxy use ``random_proxy`` function.

To iterate over random proxies use ``iter_random_proxy`` function which is generator.

Note that `proxy` is not just a "server:port". It is a tuple: (proxy, proxy_type)
By default `random_proxy()` returns proxies of two types: socks4 and socks5
"""
from grab import Grab, GrabError
import urllib
from random import sample, choice
import logging
from hashlib import sha1
import os.path
import time

import settings

# Type of proxy:
# 0 - http, 1 - ssl, 2 - ssl/http, 3 - socks4, 4 - socks5
# Anonimity level:
# "" - any, 1 - transparent, 2 - anonymous, 3 - elite

BASE_URL = 'http://worldofproxy.com/getx_%s_%d___3___.html' 
URLS = (
    #('http', 0), # http
    #('http', 1), # ssl
    ('socks4', 3),
    ('socks5', 4),
)

CACHE_TIMEOUT = 60 * 10
CACHE = []

def file_age(path):
    return time.time() - os.path.getmtime(path)


def load():
    for proxy_type, arg in URLS:
        url = BASE_URL % (settings.WORLDOFPROXY_KEY, arg)
        cache_path = 'var/proxy_%s.txt' % sha1(url).hexdigest()
        if os.path.exists(cache_path) and file_age(cache_path) < CACHE_TIMEOUT:
            logging.debug('Loading proxy list %s from cache' % proxy_type)
            data = open(cache_path).read()
        else:
            logging.debug('Loading proxy list %s' % proxy_type)
            data = urllib.urlopen(url).read()
            open(cache_path, 'w').write(data)
        items = data.splitlines()
        for item in items:
            CACHE.append((item, proxy_type))


def random_proxy(types=('socks4', 'socks5')):
    if not CACHE:
        load()
    return choice(CACHE)


def iter_random_proxy(types=('socks4', 'socks5')):
    yield random_proxy(types=types)
