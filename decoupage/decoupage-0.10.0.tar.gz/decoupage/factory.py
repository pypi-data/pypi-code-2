from web import Decoupage
from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    app = Decoupage(**app_conf)
    return HTTPExceptionHandler(app)
    
