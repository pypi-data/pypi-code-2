# -*- coding: utf-8 -*-
import jinja2
import wsgi
from config import cfg
from os.path import normpath, join, getmtime
from os import getcwd

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

    path = normpath(join(getcwd(), f.name))
    mtime = getmtime(path)
    return f.read().decode('utf-8'), path, lambda: mtime == getmtime(path)

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
            extensions = ['jinja2.ext.with_'],
        )        
        return _ENV.get_template(fn).render(context)
    
def render_to_response(rq, fn, context=None, **response_kwargs):
    context = context or {}
    for k, v in rq.context.iteritems():
        if k not in context:
            context[k] = v
    return wsgi.Response(render_to_string(fn, context), **response_kwargs)
    
