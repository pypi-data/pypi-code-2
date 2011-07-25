# Copyright (c) 2007-2011 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.core
----------

Core WSGI interface functions.
"""

__all__ = ['currentrequest', 'to_wsgi', 'response']

import sys

from itertools import chain, takewhile
try:
    from functools import partial
except ImportError:
    # Roughly equivalent implementation for Python < 2.5
    # Taken from http://docs.python.org/library/functools.html
    def partial(func, *args, **keywords):
        def newfunc(*fargs, **fkeywords):
            newkeywords = keywords.copy()
            newkeywords.update(fkeywords)
            return func(*(args + fargs), **newkeywords)
        newfunc.func = func
        newfunc.args = args
        newfunc.keywords = keywords
        return newfunc
	


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
        self.pesto_app = pesto_app
        self.app_args = app_args
        self.app_kwargs = app_kwargs
        self.bound_instance = None

    def __get__(self, obj, obj_class=None):
        """
        Descriptor protocol __get__ function, allows this decorator to be
        applied to class methods
        """
        if self.bound_instance:
            return self
        self.bound_instance = obj
        self.pesto_app = partial(self.pesto_app, obj) 
        return self

    def __call__(self, environ, start_response):
        """
        Return a callable conforming to the WSGI interface.
        """
        return _PestoWSGIAdaptor(self, environ, start_response)


class _PestoWSGIAdaptor(object):
    
    def __init__(self, decorated_app, environ, start_response):
        self.decorated_app = decorated_app
        self.environ = environ
        self.start_response = start_response
        self.request = Request(environ)
        self.content_iter = None

    def __iter__(self):
        """
        ``__iter__`` method
        """
        return self

    def next(self):
        """
        Iterator ``next`` method
        """
        if self.content_iter is None:
            args = (self.request,) + self.decorated_app.app_args
            try:
                response = self.decorated_app.pesto_app(*args, **self.decorated_app.app_kwargs)
                self.content_iter = response(self.environ, self.start_response)
            except RequestParseError, e:
                response_close = getattr(self.content_iter, 'close', None)
                if response_close is not None:
                    response_close()
                self.content_iter = e.response()(self.environ, self.start_response)
        return self.content_iter.next()

    def close(self):
        """
        WSGI iterable ``close`` method
        """
        if self.content_iter is None:
            return
        response_close = getattr(self.content_iter, 'close', None)
        if response_close is not None:
            return response_close()


from pesto import response
from pesto.request import currentrequest, Request
from pesto.httputils import RequestParseError
