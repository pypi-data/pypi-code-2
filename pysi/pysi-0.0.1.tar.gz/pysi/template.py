# -*- coding: utf-8 -*-
import jinja2
import wsgi

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


TEMPLATE_CACHE = {}
JINJA_ENV = jinja2.Environment(
    loader = jinja2.FunctionLoader(load_template),
    autoescape = True,
)

def get_template(fn):
    try:
        template = TEMPLATE_CACHE[fn]
    except KeyError:
        template = JINJA_ENV.get_template(fn)
        TEMPLATE_CACHE[fn] = template
    return template

def render_to_string(fn, context):
    return get_template(fn).render(context)
    
def render_to_response(rq, fn, context, **response_kwargs):
    rq.context.update(context)
    return wsgi.Response(render_to_string(fn, rq.context), **response_kwargs)
    
