# -*- coding: utf-8 -*-
import jinja2
import wsgi
from config import cfg

def load_template(fn):
    ERR_MSG = 'template not found: %s' % fn
    try:
        f = open('templates/%s' % fn)
    except IOError:
        try:
            app_name, fn = fn.split('/', 1)
            f = open('%s/templates/%s' % (app_name, fn))
        except (IOError, ValueError):
            assert 0, ERR_MSG
    return f.read().decode('utf-8')

def render_to_string(fn, context):
    global _ENV
    try:
        return _ENV.get_template(fn).render(context)
    except NameError:
        _ENV = jinja2.Environment(
            loader = jinja2.FunctionLoader(load_template),
            autoescape = True,
            cache_size = cfg.TEMPLATE_CACHE_SIZE,
            auto_reload = cfg.TEMPLATE_AUTO_RELOAD,
        )        
        return _ENV.get_template(fn).render(context)
    
def render_to_response(rq, fn, context, **response_kwargs):
    rq.context.update(context)
    return wsgi.Response(render_to_string(fn, rq.context), **response_kwargs)
    
