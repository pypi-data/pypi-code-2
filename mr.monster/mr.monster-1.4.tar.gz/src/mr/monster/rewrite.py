import re
from webob import Request, Response

def RewriteFactory(global_config, **local_conf):
    if "host" in local_conf:
        if "port" not in local_conf:
            raise AttributeError("You must also supply a port")

    if "port" in local_conf:
        if "host" not in local_conf:
            raise AttributeError("You must also supply a host")

    
    def factory(app):
        return RewriteMiddleware(app, **local_conf)
    return factory

_marker = object()

hostre = re.compile("(.*):(\d+)")

class RewriteMiddleware(object):
    """An endpoint"""
    
    def __init__(self, app, host=None, 
                            port=None, 
                            scheme=None,
                            internalpath='', 
                            externalpath='', 
                            autodetect=_marker):
        self.host = host
        self.port = port
        self.scheme = scheme


        # Support special case for root external path.
        if externalpath.endswith('/'):
            externalpath = externalpath[:-1]
        self.externalpath = externalpath.split("/")

        # Ignore trailing slash on internalpath
        if internalpath.endswith('/'):
            internalpath = internalpath[:-1]
        self.internalpath = internalpath.split("/")
        
        if autodetect is _marker and self.host is None and self.port is None:
            self.autodetect = True
        else:
            self.autodetect = str(autodetect).lower() == "true"
            
        self.app = app
    
    def __call__(self, environ, start_response):
        
        scheme = self.scheme
        if scheme is None:
            # wsgi.url_scheme appears to be the most standard
            # method of getting the scheme.
            scheme = environ.get("wsgi.url_scheme","http")
        
        options = {"host": self.host, 
                   "port": self.port, 
                   "scheme": scheme,
                   "inpath":"/".join(self.internalpath),
                   "outpath":"/_vh_".join(self.externalpath)}
        
        if self.autodetect:
            host = environ.get('HTTP_HOST', None)
            if host is not None:
                # Using HTTP 1.1
                parsed = hostre.search(host)
                if parsed:
                    parsed = parsed.groups()
                    options['host'] = parsed[0]
                    if options['port'] is None:
                        options['port'] = parsed[1]
                else:
                    options['host'] = host
                    if options['port'] is None:
                        options['port'] = '80'
            else:
                # HTTP 1.0 or 0.9
                host = environ['SERVER_NAME']
                options['host'] = host
                if options['port'] is None:
                    options['port'] = environ['SERVER_PORT']
        
    
        if "SCRIPT_NAME" in environ:
            options['PATH_INFO'] = environ['SCRIPT_NAME']
            environ['SCRIPT_NAME'] = ''
        else:
            options['PATH_INFO'] = ''
        
        options['PATH_INFO'] += environ['PATH_INFO']
        
        op = '/'.join(self.externalpath)
        if options['PATH_INFO'].startswith(op):
            pl = len(op)
            options['PATH_INFO'] = options['PATH_INFO'][pl:]
        
        format = "/VirtualHostBase/%(scheme)s/"   \
                 "%(host)s:%(port)s"        \
                 "%(inpath)s"              \
                 "/VirtualHostRoot"         \
                 "%(outpath)s"             \
                 "%(PATH_INFO)s"    % options
        
        if options['host'] is not None:
            environ['PATH_INFO'] = format
        
        request = Request(environ)
        response = request.get_response(self.app)
        return response(environ, start_response)
