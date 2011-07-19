"""
request dispatcher for uploader
"""

import os
from handlers import Get, Post, SubpathGet, SubpathPost
from webob import Request, exc

class Dispatcher(object):

    ### class level variables
    defaults = { 'directory': None,
                 'auth': False,
                 'query_string': None,
                 'subpath': False,
                 'display_contents': False,
                 'app': None,
                 'log_file': None}

    def __init__(self, **kw):

        # set defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        assert os.path.exists(self.directory), "The base directory %s does not exist; uploader needs it!" % self.directory
        if self.app:
            assert hasattr(self.app, '__call__'), "app must be a callable WSGI app"

        # set True/False values
        for i in ('auth', 'subpath', 'display_contents'):
            attr = getattr(self, i)
            if isinstance(attr, basestring):
                setattr(self, i, attr.lower() == 'true')

        # choose handler based on subpath
        if self.subpath:
            self.handlers = [ SubpathGet, SubpathPost ]
        else:
            self.handlers = [ Get, Post ]

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)
        if self.auth and not request.remote_user:
            return exc.HTTPUnauthorized()(environ, start_response)
        for h in self.handlers:
            if h.match(self, request):
                handler = h(self, request)
                break
        else:
            if self.app:
                return self.app(environ, start_response)
            handler = exc.HTTPNotFound
        res = handler()
        return res(environ, start_response)
