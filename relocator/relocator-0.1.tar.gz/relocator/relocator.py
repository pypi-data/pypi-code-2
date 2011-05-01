"""
request dispatcher
"""

import urlparse
from webob import Request

class Relocator(object):


    def __init__(self, app, baseurl):
        self.app = app
        self.baseurl = list(urlparse.urlsplit(baseurl))

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = request.get_response(self.app)
        if 'Location' in response.headers:
            parsed = list(urlparse.urlsplit(response.headers['Location']))
            location = ['' for i in range(5)] # new location
            
            # overwrite scheme, netloc, and fragment
            for i in (0, 1, 4): 
                location[i] = self.baseurl[i]

            # append path and query string
            for i in (2, 3):
                location[i] = self.baseurl[i] + parsed[i]

            response.headers['Location'] = urlparse.urlunsplit(location)
        return response(environ, start_response)
