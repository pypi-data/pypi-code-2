from webob import Request
import warnings
from urlparse import urlparse
from paste.recursive import ForwardRequestException, RecursiveMiddleware
from paste.util import converters
from paste.response import replace_header

class ForwardFriendlyStatusKeeper(object):
    """A version of the StatusKeeper from paste.errordocument that allows
    301 and 302 responses to bubble up.
    """
    def __init__(self, app, status, url, headers):
        self.app = app
        self.status = status
        self.url = url
        self.headers = headers

    def __call__(self, environ, start_response):
        
        def keep_status_start_response(status, headers, exc_info=None):
            for header, value in headers:
                if header.lower() == 'set-cookie':
                    self.headers.append((header, value))
                else:
                    replace_header(self.headers, header, value)
            
            if not (status.startswith('302') or status.startswith('301')):
                status = self.status
            return start_response(status, self.headers, exc_info)
        
        parts = self.url.split('?')
        environ['PATH_INFO'] = parts[0]
        if len(parts) > 1:
            environ['QUERY_STRING'] = parts[1]
        else:
            environ['QUERY_STRING'] = ''
        
        return self.app(environ, keep_status_start_response)
        
class ForwardFriendlyStatusBasedForward(object):
    """A version of StatusBasedForward from paste.errordocument that allows
    301 and 302 responses to bubble up.
    """

    def __init__(self, app, mapper, global_conf=None, **params):
        if global_conf is None:
            global_conf = {}
        # @@: global_conf shouldn't really come in here, only in a
        # separate make_status_based_forward function
        if global_conf:
            self.debug = converters.asbool(global_conf.get('debug', False))
        else:
            self.debug = False
        self.application = app
        self.mapper = mapper
        self.global_conf = global_conf
        self.params = params

    def __call__(self, environ, start_response):
        url = []
        
        def change_response(status, headers, exc_info=None):
            status_code = status.split(' ')
            try:
                code = int(status_code[0])
            except (ValueError, TypeError):
                raise Exception(
                    'ForwardFriendlyStatusBasedForward middleware '
                    'received an invalid status code %s'%repr(status_code[0])
                )
            message = ' '.join(status_code[1:])
            new_url = self.mapper(
                code, 
                message, 
                environ, 
                self.global_conf, 
                **self.params
            )
            if not (new_url == None or isinstance(new_url, str)):
                raise TypeError(
                    'Expected the url to internally '
                    'redirect to in the ForwardFriendlyStatusBasedForward mapper'
                    'to be a string or None, not %s'%repr(new_url)
                )
            if new_url:
                url.append([new_url, status, headers])
            else:
                return start_response(status, headers, exc_info)

        app_iter = self.application(environ, change_response)
        if url:
            if hasattr(app_iter, 'close'):
                app_iter.close()
            
            # Preserve path and query string
            request = Request(environ)
            environ['collective.fourohfour.original_path'] = request.path
            environ['collective.fourohfour.original_path_qs'] = request.path_qs
            
            def factory(app):
                return ForwardFriendlyStatusKeeper(app, status=url[0][1], url=url[0][0], headers=url[0][2])
            raise ForwardRequestException(factory=factory)
        else:
            return app_iter

def forward(app, codes):
    """A version of forward() from paste.errordocument that preserves
    the original path and query string in the environment under the keys
    collective.fourohfour.original_path and
    collective.fourohfour.original_path_qs.
    
    It will also prefix a VHM root set with repoze.vhm to be prefixed to
    the target path, for transparent virtual hosting support.
    
    Finally, this middleware uses the  ForwardFriendlyStatusBasedForward
    above to allow the error handle to raise 301 or 302 responses.
    """
    for code in codes:
        if not isinstance(code, int):
            raise TypeError('All status codes should be type int. '
                '%s is not valid'%repr(code))
                
    def error_codes_mapper(code, message, environ, global_conf, codes):
        if codes.has_key(code):
            vhm_root = environ.get('repoze.vhm.virtual_root', '')
            target = codes[code]
            
            if vhm_root:
                target = vhm_root + target
            
            return target
        else:
            return None

    return RecursiveMiddleware(
        ForwardFriendlyStatusBasedForward(
            app, 
            error_codes_mapper, 
            codes=codes,
        )
    )

def make_handler(app, global_conf, **kw):
    """
    Paste Deploy entry point to create a error document wrapper.
    
    This should normally sit just before Paste#httpexceptions.  
    
    This middleware is a copy of Paste#errordocument, except it
    preserves more information about the original request and
    handles 301/302 redirect responses sent by the error handler.
    
    Use like::

        [filter-app:main]
        use = egg:collective.fourohfour#errorhandler
        next = error
        404 = /@@404-error
        500 = /standard_error_message
        
    If no codes are set, the mapping shown above will be used.
    These should be appropriate for a Plone site virtual-hosted
    at the root of the domain being used, with collective.fourohfour
    installed.
    """
    map = {}
    
    if not kw:
        kw = {
                '404': '/@@404-error',
                '500': '/standard_error_message'
            }
    
    for status, redir_loc in kw.items():
        try:
            status = int(status)
        except ValueError:
            raise ValueError('Bad status code: %r' % status)
        map[status] = redir_loc
    forwarder = forward(app, map)
    return forwarder
