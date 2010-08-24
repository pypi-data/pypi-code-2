import re
from webob import Request, Response

def DropFactory(global_config, **local_conf):
    def factory(app):
        return DropMiddleware(app, **local_conf)
    return factory

class DropMiddleware(object):
    """An endpoint"""
    
    def __init__(self, app, SCRIPT_NAME=None):
        self.SCRIPT_NAME = SCRIPT_NAME
        self.app = app
    
    def __call__(self, environ, start_response):
        
        if self.SCRIPT_NAME is not None:
            environ['SCRIPT_NAME'] = self.SCRIPT_NAME
        
        if environ['SCRIPT_NAME'] == '/':
            environ['SCRIPT_NAME'] = ''
        
        request = Request(environ)
        response = request.get_response(self.app)
        return response(environ, start_response)
