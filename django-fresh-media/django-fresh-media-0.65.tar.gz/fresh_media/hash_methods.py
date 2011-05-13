from __future__ import with_statement
from django.conf import settings
from django.core.cache import cache

import os.path
from hashlib import md5

# Default settings
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)
METHOD = getattr(settings, 'FRESH_MEDIA_METHOD', 'mtime').lower()
CACHE = int(getattr(settings, 'FRESH_MEDIA_CACHE_FOR', 0))
RAW = getattr(settings, 'FRESH_MEDIA_RAW', False)
FAIL_IF_NON_EXIST = getattr(settings, 'FRESH_MEDIA_FAIL_IF_NO_EXIST', True)


def method_md5(path):
    """Method to get hash, based on md5 sum of file content"""
    with open(path) as f:
        hash = md5(f.read()).hexdigest()
        if RAW:
            return hash
        else:
            return int(hash, 16)


methods = {
    # Inline method to get hash, based on file last modificatin time.
    'mtime': lambda path: int(os.path.getmtime(path)),
    'md5': method_md5,
    # Inline method to get hash, based on file size.
    'size': lambda path: os.path.getsize(path),
}


def convert(f):
    """Convert given int nuber from base 10 to base 62"""
    def wrap(path):
        num = f(path)
        st = ""
        while num:
            num, code = divmod(num, BASE)
            st += ALPHABET[code]
        return st
    return wrap


def cached(f):
    """Cache file hash for reduce disk io."""
    def wrap(path):
        cached_result = cache.get(path, None)
        if cached_result is None:
            result = f(path)
            cache.set(path, result, CACHE)
            return result
        else:
            return cached_result
    return wrap

get_token = methods[METHOD]

if CACHE > 0:
    get_token = cached(get_token)

if not RAW:
    get_token = convert(get_token)
