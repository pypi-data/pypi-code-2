"""
example app for how to use TypedTransformer TTW on a directory
"""

import os

from contenttransformer.app import FileTypeTransformer
from webob import Request, exc

class Dispatcher(object):

    ### class level variables
    defaults = { 'app': None, 
                 'directory': None, 
                 'transforms': ''}

    def __init__(self, **kw):
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        assert os.path.exists(self.directory)
        self.transforms = [ [j.strip() for j in i.split('=', 1) ] for i in self.transforms.split(',') if '=' in i]
        self.transformer = FileTypeTransformer(*self.transforms)
        if self.app:
            assert hasattr(self.app, '__call__')

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)
        path = os.path.join(self.directory, request.path_info.strip('/'))
        if os.path.exists(path) and os.path.isfile(path):
            handler = self.transformer(path)
            return handler(environ, start_response)
        else:
            # TODO: if self.app ... 
            return exc.HTTPNotFound()(environ, start_response)
