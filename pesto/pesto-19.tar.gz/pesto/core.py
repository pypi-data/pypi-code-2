# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.core
----------

Core WSGI interface functions.
"""

__all__ = ['currentrequest', 'to_wsgi', 'response']

import sys

from itertools import chain, takewhile

from pesto import response
from pesto.request import currentrequest, Request
from pesto.httputils import RequestParseError


def to_wsgi(pesto_app):
    """
    A decorator function, equivalent to calling
    ``PestoWSGIApplication(pesto_app)`` directly.
    """
    return PestoWSGIApplication(pesto_app)

class PestoWSGIApplication(object):
    """
    A WSGI application wrapper around a Pesto handler function.

    The handler function should have the following signature:

        pesto_app(request) -> pesto.response.Response

    Synopsis::

        >>> from pesto.testing import TestApp
        >>> from pesto.response import Response
        >>> 
        >>> def handler(request):
        ...     return Response([u"Whoa nelly!"])
        ...
        >>> wsgiapp = PestoWSGIApplication(handler)
        >>> print TestApp(wsgiapp).get().headers
        [('Content-Type', 'text/html; charset=UTF-8')]
        >>> print TestApp(wsgiapp).get()
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Whoa nelly!
    """

    def __init__(self, pesto_app, *app_args, **app_kwargs):
        """
        Initialize an instance of ``PestoWSGIApplication``.
        """
        self._pesto_app = pesto_app
        self._app_args = app_args
        self._app_kwargs = app_kwargs
        self._content_iter = None
        self._instance = None
        self.environ = None
        self.start_response = None
        self.request = None

    def __call__(self, environ, start_response):
        """
        WSGI callable - take ``pesto_app`` and adapt it to the WSGI interface.
        """
        self._content_iter = None
        self.environ = environ
        self.start_response = start_response
        self.request = Request(environ)
        return self

    def __get__(self, obj, obj_class=None):
        self._instance = obj
        return self

    def __iter__(self):
        """
        ``__iter__`` method
        """
        return self

    def next(self):
        """
        Iterator ``next`` method
        """
        if self._content_iter is None:
            if self._instance is not None:
                args = (self._instance, self.request) + self._app_args
            else:
                args = (self.request,) + self._app_args
            try:
                response = self._pesto_app(*args, **self._app_kwargs)
                self._content_iter = response(self.environ, self.start_response)
            except RequestParseError, e:
                response_close = getattr(self._content_iter, 'close', None)
                if response_close is not None:
                    response_close()
                self._content_iter = e.response()(self.environ, self.start_response)
        return self._content_iter.next()

    def close(self):
        """
        WSGI iterable ``close`` method
        """
        if self._content_iter is None:
            return
        response_close = getattr(self._content_iter, 'close', None)
        if response_close is not None:
            return response_close()

