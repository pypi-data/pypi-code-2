import os

import static
from pystynamic.generation import SiteGenerator
from pystynamic.exceptions import ResourceNotFound

class PystynamicWSGIApp(object):
    def __init__(self, root_path):
        self.root_path = root_path
        self.static_app = static.Cling(self.root_path)

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        if path_info.startswith('/static') or path_info in ['/favicon.ico']:
            return self.static_app(environ, start_response)
        else:
            generator = SiteGenerator.build_for_path(self.root_path)
            try:
                results = generator.generate_resource(path_info)
                status = '200 Ok'
            except ResourceNotFound:
                results = u'404 Not Found'
                status = '404 Not Found'

            response_headers = [('Content-type', 'text/html; charset=utf8')]
            start_response(status, response_headers)
            return [results.encode('utf8')]
            
        
