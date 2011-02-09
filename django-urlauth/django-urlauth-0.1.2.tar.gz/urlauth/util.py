import os
from datetime import datetime
import time
from base64 import b64encode, b64decode
from urllib import urlencode
from cgi import parse_qs

from django.conf import settings

from urlauth.models import AuthKey


class InvalidKey(Exception):
    pass


def wrap_url(url, **kwargs):
    """
    Create new authorization key and append it to the url.
    """

    if not 'uid' in kwargs:
        raise Exception('wrap_url function requires uid name argument')

    hash = AuthKey.objects.create_key(**kwargs)
    clue = '?' in url and '&' or '?'
    url = '%s%s%s=%s' % (url, clue, settings.URLAUTH_AUTHKEY_NAME, hash)
    return url


def load_key(hash):
    """
    Load key record associated with given hash.
    """

    try:
        key = AuthKey.objects.get(pk=hash)
    except AuthKey.DoesNotExist:
        raise InvalidKey('Key does not exist')
    if datetime.now() > key.expired:
        raise InvalidKey('Key is expired')
    return key
