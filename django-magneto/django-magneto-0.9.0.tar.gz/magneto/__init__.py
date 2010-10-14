import hashlib

from django.conf import settings


def cache_key(name):
    """
    Create a cache key based on the template name and the current site id.
    """
    return hashlib.md5("magneto-%s-%s" % (name, settings.SITE_ID)).hexdigest()
