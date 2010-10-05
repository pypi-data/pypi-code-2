# -*- coding: utf-8 -*-
import wsgi


class NotFound(Exception):
    pass

class Redirect(Exception):
    def __init__(self, url, **kwargs):
        self.res = wsgi.Response('', code=302, headers={'Location': url}, **kwargs)

class PermanentRedirect(Exception):
    def __init__(self, url, **kwargs):
        self.res = wsgi.Response('', code=301, headers={'Location': url}, **kwargs)

class BasicAuth(Exception):
    def __init__(self):
        self.res = wsgi.Response('Authorization Error', 
            code=401, content_type='text/plain',
            headers={'WWW-Authenticate' : 'Basic realm="Enter password"'},
        )
