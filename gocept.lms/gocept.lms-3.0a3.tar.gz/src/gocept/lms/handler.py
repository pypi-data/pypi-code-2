# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Base handler code."""

import grok
import gocept.lms.interfaces
import urlparse
import urllib


class AbstractURLHandler(object):
    """Abstract base handler implementation for URIs that are URLs.
    
    Subclasses need to implement `check`.

    """

    grok.provides(gocept.lms.interfaces.ISchemeHandler)

    def allow(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        if not netloc:
            return False
        host, port = urllib.splitport(netloc)
        return gocept.lms.filter.allow_host(host)

    def classify(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        if netloc:
            host, port = urllib.splitport(netloc)
            return host
