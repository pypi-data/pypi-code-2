# -*- coding: utf-8 -*-
import wsgi


class NotFound(Exception):
    pass

class Redirect(Exception):
    '''Deprecated'''
    def __init__(self, url, **kwargs):
        self.res = wsgi.redirect(url, **kwargs)

class PermanentRedirect(Exception):
    '''Deprecated'''
    def __init__(self, url, **kwargs):
        self.res = wsgi.redirect(url, permanent=True, **kwargs)

class BasicAuth(Exception):
    def __init__(self):
        self.res = wsgi.Response('Authorization Error', 
            code=401, content_type='text/plain',
            headers={'WWW-Authenticate' : 'Basic realm="Enter password"'},
        )
