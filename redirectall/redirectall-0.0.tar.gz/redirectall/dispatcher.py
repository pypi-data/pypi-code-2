"""
request dispatcher
"""

from webob import Request, exc

class RedirectAll(object):

    ### class level variables

    def __init__(self, base_url):
        self.base_url = base_url

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)
        location = self.base_url + request.path
        if request.query_string:
            location += '?' + request.query_string
        response = exc.HTTPMovedPermanently(location=location)
        return response(environ, start_response)
