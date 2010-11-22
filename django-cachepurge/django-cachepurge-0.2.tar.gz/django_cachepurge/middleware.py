# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import get_script_prefix
from django_cachepurge import clear_urls, get_urls
from django_cachepurge.utils import pruneAsync

CACHE_URLS = settings.CACHE_URLS

if isinstance(CACHE_URLS, basestring):
    CACHE_URLS = (CACHE_URLS,)

class CachePurge(object):
    """ Middleware responsible of sending PURGE to upstream cache(s)
    """
    def process_request(self, request):
        clear_urls()

    def process_response(self, request, response):

        prefix = get_script_prefix()
        for url in get_urls():
            if url.startswith(prefix):
                # convert absolute url into a relative one
                url = url.replace(prefix, u'/', 1)
            for cache in CACHE_URLS:
                url_in_cache = "%s%s" % (cache, url)

                pruneAsync(url_in_cache)

        return response
