from web import Dispatcher
from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    keystr = 'transformer.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = Dispatcher(**args)
    return HTTPExceptionHandler(app)
    
