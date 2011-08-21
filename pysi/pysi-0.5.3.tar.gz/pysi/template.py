# -*- coding: utf-8 -*-
from os import getcwd
from os.path import normpath, join, getmtime

try:
    import jinja2
except ImportError, ex:
    jinja2_ex = ex
import wsgi
from config import cfg
from util import obj_from_str


def file_loader(fn):
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
    return f.read().decode('utf-8'), path, lambda: mtime == getmtime(path)

def render_to_string(fn, context):
    global _ENV
    try:
        try:
            return _ENV.get_template(fn).render(context)
        except EOFError:
            raise NameError
    except NameError:
        try:
            _ENV = jinja2.Environment(
                loader = jinja2.FunctionLoader(obj_from_str(cfg.TEMPLATE_LOADER)),
                autoescape = True,
                cache_size = cfg.TEMPLATE_CACHE_SIZE,
                auto_reload = cfg.TEMPLATE_AUTO_RELOAD,
                extensions = ['jinja2.ext.with_'],
            )
        except NameError:
            raise jinja2_ex
        return _ENV.get_template(fn).render(context)
    
def render_to_response(rq, fn, context=None, **response_kwargs):
    context = context or {}
    for k, v in rq.context.iteritems():
        if k not in context:
            context[k] = v
    return wsgi.Response(render_to_string(fn, context), **response_kwargs)

    
