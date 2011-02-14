import base64
import time
import urlparse
import urllib
import httplib2
try:
    import json
except ImportError:
    import simplejson as json

# Python 2.5 compat fix
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl

from socialtext import __version__ as api_version
from socialtext import exceptions

class SocialtextClient(httplib2.Http):
    
    USER_AGENT = 'python-socialtext.api/%s' % api_version
    
    def __init__(self, server, user, password):
        super(SocialtextClient, self).__init__()
        self.server = server
        self.user = user
        self.password = password

        # httplib2 overrides
        self.force_exception_to_status_code = True

    def request(self, *args, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Accept', 'application/json')
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        
        if self.user and self.password:
            kwargs['headers']['authorization'] = self.authorization()

        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['body'] = json.dumps(kwargs['body'])
        resp, body = super(SocialtextClient, self).request(*args, **kwargs)

        if resp.status in (400, 401, 403, 404, 413, 500):
            raise exceptions.from_response(resp, body)

        if body and kwargs['headers']['Accept'] == 'application/json':
            body = json.loads(body)
        
        return resp, body

    def authorization(self):
        return 'Basic ' + base64.b64encode("%s:%s" % (self.user, self.password))

    def _st_request(self, path, method, **kwargs):
        url = self.server
        if not url[-1] == "/":
            url += "/"
        if path[0] == "/":
            url += path[1:]
        else:
            url += path 
        resp, body = self.request(url, method, **kwargs)
        return resp, body

    def get(self, url, **kwargs):
        return self._st_request(url, 'GET', **kwargs)
    
    def post(self, url, **kwargs):
        return self._st_request(url, 'POST', **kwargs)
    
    def put(self, url, **kwargs):
        return self._st_request(url, 'PUT', **kwargs)
    
    def delete(self, url, **kwargs):
        return self._st_request(url, 'DELETE', **kwargs)