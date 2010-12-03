import logging

from webob import Request, Response, exc
from webob.descriptors import environ_getter
from webob.exc import *

from rum.exceptions import ConfigError

__all__ = ["RumRequest", "RumResponse"]
__all__.extend(exc.__all__)

log = logging.getLogger(__name__)

class RumRequest(Request):
    

    def _get_routes(self):
        return self.environ.get('rum.routes', {})
    def _set_routes(self, d):
        self.environ['rum.routes']  = d
    routes = property(_get_routes, _set_routes)

    def next_redirect(self):
        if 'rum.next_redirect' not in self.environ:
            old_method = self.method
            if self.method not in ['POST','GET']:
                self.method = 'POST'
            try:
                input = getattr(self, self.method.upper()).mixed()
                next_redirect = input.get('_next_redirect')
                if next_redirect and self.host in next_redirect:
                    abs_part = self.scheme + '://' + self.host
                    next_redirect = next_redirect[len(abs_part):]
                self.environ['rum.next_redirect'] = next_redirect
            finally:
                self.method = old_method
        return self.environ['rum.next_redirect']
    next_redirect = property(fget=next_redirect, doc="""\
        The Location URL a redirect-after-post whould point to. It defaults to
        the referer if it is not overriden by the client through a '_next' query
        string argument on GET or '_next' argument on the body of a urlencoded
        POST payload.""")
        
    @property
    def session(self):
        try:
            return self.environ['beaker.session']
        except KeyError:
            raise ConfigError("Beaker session middleware needs to be available")

    current_user = environ_getter('rum.user', None)
    
class RumResponse(Response):
    charset = 'utf-8'
