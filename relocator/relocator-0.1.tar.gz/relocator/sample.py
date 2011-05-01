#!/usr/bin/env python

from relocator import Relocator
from webob import exc

def sample_app(environ, start_response):
    """sample app that does a redirect"""
    response = exc.HTTPSeeOther(location='/foo/bar')
    return response(environ, start_response)

def sample_factory(baseurl='http://example.com/toolbox'):
    """create a webob view and wrap it in the relocator"""
    return Relocator(sample_app, baseurl)

if __name__ == '__main__':
   from wsgiref import simple_server
   app = sample_factory()
   server = simple_server.make_server(host='0.0.0.0', port=12345, app=app)
   server.serve_forever()
