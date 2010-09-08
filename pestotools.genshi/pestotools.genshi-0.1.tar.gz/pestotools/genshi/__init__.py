from functools import wraps

import genshi.template.loader
import genshi.template.markup
import genshi.template.text
import genshi.core
from genshi.template.base import Template
from genshi.filters import HTMLFormFiller

from genshi.template.markup import MarkupTemplate

from pesto import currentrequest
from pesto.response import Response

__all__ = ['render_docstring', 'render', 'select', 'genshi', 'formfilled']

# Default template loader to use by default. You may replace this with a
# template loader configured with an appropriate search path for your
# application.
TEMPLATE_LOADER = genshi.template.loader.TemplateLoader(['.'])

# Default variables passed to ALL templates. You can replace this either with a
# dictionary or with a callable returning a dictionary.
TEMPLATE_VARS = {}

def render_docstring(loader=None, cls=MarkupTemplate):
    u"""
    Render the function's docstring as a genshi template stream
    """
    def render_docstring(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            template = MarkupTemplate(
                func.func_doc,
                loader=loader or TEMPLATE_LOADER
            )
            data = func(*args, **kwargs)
            if isinstance(data, Response):
                return data
            if data is None:
                data = {}
            return _genshi_stream(template, **data)
        return decorated
    return render_docstring

def render(template_path=None, loader=None, cls=MarkupTemplate):
    """
    Render the function's output as an unserialized Genshi template stream
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            data = func(*args, **kwargs)
            if isinstance(data, Response):
                return data

            _template_path = template_path
            if template_path is None:
                _template_path, data = data

            return _genshi_stream(_template_path, **data)
        return decorated
    return decorator

def select(path):
    """
    Take a function emitting a genshi stream and apply an XPATH select to it to
    filter out all but the selected elements.
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, Response):
                return result
            return result.select(path)
        return decorated
    return decorator

def genshi(content_type='text/html; charset=UTF-8'):
    """
    Take a function emitting a genshi stream, serialize it and return a pesto
    Response object.
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, Response):
                return result
            return Response(
                content = [result.render('xhtml')],
                content_type = content_type
            )
        return decorated
    return decorator

def _genshi_stream(template_path, loader=None, cls=MarkupTemplate, **kwargs):
    if isinstance(template_path, Template):
        template = template_path
    else:
        template = (loader or TEMPLATE_LOADER).load(template_path, cls=cls)
    ns = {'request': currentrequest()}
    if TEMPLATE_VARS:
        if callable(TEMPLATE_VARS):
            ns.update(TEMPLATE_VARS())
        else:
            ns.update(TEMPLATE_VARS)
    ns.update(kwargs)
    return template.generate(**ns)

def formfilled(defaults=None, form_id=None, form_name=None, source='form', **kwdefaults):
    """
    Apply the genshi ``HTMLFormFiller`` filter to a genshi stream.

    defaults:
        dictionary of default form values
    form_id
        HTML id attribute of the form
    form_name
        HTML name attribute of the form
    source
        Name of the data source on the request object, ie ``'form'`` (for
        ``request.form``) or ``'query'`` (for ``request.query``).
    **kwdefaults
        Additional defaults passed as keyword arguments
    """

    if defaults is None:
        defaults = {}

    def formfilled(func):
        @wraps(func)
        def formfilled(*args, **kwargs):
            request = currentrequest()
            data = {}
            _defaults = defaults() if callable(defaults) else defaults
            _defaults.update(kwdefaults)
            for item, default in _defaults.items():
                data[item] = default() if callable(default) else default
            source_ob = getattr(request, source)
            for k in source_ob.keys():
                l = source_ob.getlist(k)
                if len(l) == 1:
                    data[k] = l[0]
                else:
                    data[k] = l
            stream = func(*args, **kwargs)
            if isinstance(stream, Response):
                return stream
            return stream | HTMLFormFiller(name=form_name, id=form_id, data=data)
        return formfilled
    return formfilled


