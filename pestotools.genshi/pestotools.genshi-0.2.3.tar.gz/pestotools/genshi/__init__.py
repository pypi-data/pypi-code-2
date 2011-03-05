"""
Decorators and utility functions to integrate pesto handlers with the Genshi
templating system.
"""

import os
from functools import wraps, partial
from collections import Mapping

from genshi.template.loader import TemplateLoader, TemplateNotFound
from genshi.core import Stream
from genshi.template.base import Template
from genshi.template.markup import MarkupTemplate
from genshi.template.text import NewTextTemplate as TextTemplate
from genshi.filters import HTMLFormFiller

from pesto import currentrequest, to_wsgi
from pesto.wsgiutils import normpath as wsgi_normpath
from pesto.response import Response

__all__ = [
    'GenshiRender','select', 'formfilled', 'GenshiApp', 'genshi_app_factory'
]

def _make_decorator(render_method, template, *args, **kwargs):
    """
    Return a decorator wrapping a function so that it's return value is passed
    as the data paramter to ``render_method``
    """
    def decorator(func):
        @wraps(func)
        def decorated(*fargs, **fkwargs):
            data = func(*fargs, **fkwargs)
            if template is None:
                try:
                    local_template, data = data
                except (TypeError, ValueError):
                    return data
            else:
                local_template = template
            if data is None:
                data = {}

            # Pass through any response that is not a mapping
            if not isinstance(data, Mapping):
                return data

            return render_method(
                local_template, data, _in_decorator=True,
                *args, **kwargs
            )
        return decorated
    return decorator

class GenshiIter(object):
    """
    Wrap a genshi stream so that it can be used as a WSGI response iterator.
    The underlying genshi stream remains accessible via the .stream property
    """

    def __init__(self, stream, serializer='xhtml'):
        self.stream = stream
        self.serializer = serializer

    def __iter__(self):
        return iter([self.stream.render(self.serializer)])

class GenshiRender(object):
    """
    A GenshiRender instance provides decorators and functions for rendering
    Genshi templates to pesto Response objects or to strings.

    There are methods to render using both Genshi's MarkupTemplate or
    TextTemplate, and to return the result as a string, a genshi stream, or a
    response object.

    This example shows the class being used as a decorator. Calling ``myfunc``
    will return a pesto.response.Response object to be returned with the
    contents of 'page.html' rendered with the variables provided in the return
    value of ``myfunc``::

        >>> render = GenshiRender(TemplateLoader(['path/to/templates/']))
        >>> @render('page.html')
        ... def myfunc():
        ...     return {'x': 'foo', 'y': 'bar'}
        ...

    Instead of rendering a response object directly it's also possible to
    simply return the rendered value as string::

        >>> @render.as_string('page.html')
        ... def myfunc():
        ...     return {'x': 'foo', 'y': 'bar'}
        ...

    For rapid prototyping, it's also possible to render function docstrings as Genshi templates::

        >>> @render.docstring()
        ... def myfunc():
        ...    '''   
        ...    <html>
        ...        $foo
        ...    </html>
        ...    '''
        ...    return {'foo': 'bar'}


    Each of the rendering methods can also be called as a regular (non-decorator) method, for example::

        >>> render.as_string('page.html', {'foo': 'bar'})

    """


    def __init__(
        self,
        loader = TemplateLoader(['.']),
        default_vars=None,
        template_cls=MarkupTemplate,
        serializer='xhtml',
    ):
        """
        Initialize a GenshiRender object.

        loader
            A TemplateLoader instance

        default_vars
            A dictionary of default values to pass to all templates. These
            values will be merged with the returned dictionaries from decorated
            methods. This can also be a callable, in which case it will be
            called every time a template is rendered to generate the default
            dictionary of template variables.

        template_cls
            The Genshi template class to use, by default ``MarkupTemplate``

        serializer
            The Genshi serializer to use, by default ``'xhtml'``
        """
        self.loader = loader
        self.default_vars = default_vars if default_vars else {}
        self.template_cls = template_cls
        self.serializer = serializer

    def as_stream(self, template=None, data=None, filters=[], template_cls=None, _in_decorator=False):
        """
        Return a Genshi stream for the rendered template
        """
        template_cls = template_cls if template_cls else self.template_cls
        if data is None and not _in_decorator:
            return _make_decorator(self.as_stream, template, filters, template_cls)

        ns = {}
        if callable(self.default_vars):
            ns.update(self.default_vars())
        else:
            ns.update(self.default_vars)

        ns.update(data)

        if not isinstance(template, Template):
            template = self.loader.load(template, cls=template_cls)

        stream = template.generate(**ns)
        for item in filters:
            stream = stream.filter(item)
        return stream

    def text_as_stream(self, *args, **kwargs):
        """
        Same as ``as_stream`` but use a Genshi TextTemplate
        """
        return self.as_stream(template_cls=TextTemplate, *args, **kwargs)

    def as_string(self, template=None, data=None, serializer=None, filters=[], template_cls=None, _in_decorator=False):
        """
        Return the string output of the rendered template.
        Can also work as a function decorator
        """
        serializer = serializer if serializer else self.serializer
        template_cls = template_cls if template_cls else self.template_cls
        if data is None and not _in_decorator:
            return _make_decorator(self.as_string, template, serializer, filters, template_cls)
        return self.as_stream(template, data, filters, template_cls).render(serializer, encoding=None)

    def text_as_string(self, *args, **kwargs):
        """
        Same as ``as_string`` but use a Genshi TextTemplate and text serializer
        """
        return self.as_string(template_cls=TextTemplate, serializer='text', *args, **kwargs)

    def as_response(self, template=None, data=None, serializer=None, filters=[], template_cls=None, _in_decorator=False, **response_kwargs):
        """
        Return a response object for the rendered template::

            >>> render = GenshiRender(TemplateLoader(['.']))
            >>> response = render.as_response('my_template.html', {'foo': 'bar'})

        Can also be used as a decorator. The decorated function will merge the original
        function's return value (a dict) with the specified template::

            >>> from pestotools.genshi import GenshiRender
            >>> from pesto import currentrequest
            >>> render = GenshiRender(TemplateLoader(['.']))
            >>> 
            >>> @render.as_response('my_template.html')
            ... def handler(request):
            ...     return {'foo': 'bar'}
            ...
        """
        serializer = serializer if serializer else self.serializer
        template_cls = template_cls if template_cls else self.template_cls
        if data is None and not _in_decorator:
            return _make_decorator(self.as_response, template, serializer, filters, template_cls, **response_kwargs)
        return Response(
            content=GenshiIter(self.as_stream(template, data, filters, template_cls), serializer),
            **response_kwargs
        )

    __call__ = as_response

    def text_as_response(self, *args, **kwargs):
        """
        Same as ``as_string`` but use a Genshi TextTemplate and text serializer
        """
        return self.as_string(template_cls=TextTemplate, serializer='text', *args, **kwargs)

    def docstring(self, serializer=None, filters=[], template_cls=None, **response_kwargs):
        """
        Render the function's docstring as a genshi template stream::

            >>> render = GenshiRender()
            >>> @render.docstring()
            ... def myhandler(request):
            ...     '''
            ...     <html>
            ...         $foo
            ...     </html>
            ...     '''
            ...     return {'foo': 'bar'}
        """
        template_cls = template_cls if template_cls else self.template_cls
        serializer = serializer if serializer else self.serializer

        def docstring(func):
            template = template_cls(
                func.func_doc,
                loader=self.loader,
            )
            return _make_decorator(self.as_response, template, serializer, filters, **response_kwargs)(func)
        return docstring

    def docstring_as_string(self, serializer=None, filters=[], template_cls=None, **response_kwargs):
        """
        Render the function's docstring as a genshi template stream::

            >>> render = GenshiRender()
            >>> @render.docstring_as_string()
            ... def myfunc():
            ...     '''
            ...     <html>
            ...         $foo
            ...     </html>
            ...     '''
            ...     return {'foo': 'bar'}
        """
        template_cls = template_cls if template_cls else self.template_cls
        serializer = serializer if serializer else self.serializer

        def docstring(func):
            template = template_cls(
                func.func_doc,
                loader=self.loader,
            )
            return _make_decorator(self.as_string, template, serializer, filters, **response_kwargs)(func)
        return docstring

def select(path):
    """
    Take a function emitting a genshi stream and apply an XPATH select to it to
    filter out all but the selected elements, eg::

        >>> render = GenshiRender()
        >>> @select("//p[@id='content']")
        ... @render.docstring()
        ... def myfunc():
        ...     '''
        ...     <html>
        ...         <h1>Welcome to $foo!</h1>
        ...         <p id="content">$foo<p>
        ...     </html>
        ...     '''
        ...     return {'foo': 'bar'}
        ...
        >>> myfunc().content
        ['<p id="content">bar</p>']
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                stream = result.content.stream
            except AttributeError:
                return result
            return result.replace(
                content=GenshiIter(stream.select(path), result.content.serializer)
            )
        return decorated
    return decorator

def formfilled(defaults=None, form_id=None, form_name=None, source='form', **kwdefaults):
    """
    Apply the genshi ``HTMLFormFiller`` filter to a genshi stream, populating
    form fields from the request object or other specified defaults.

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
            result = func(*args, **kwargs)
            try:
                stream = result.content.stream
            except AttributeError:
                return result
            data = {}
            _defaults = defaults() if callable(defaults) else defaults
            _defaults.update(kwdefaults)
            for item, default in _defaults.items():
                data[item] = default() if callable(default) else default
            source_ob = getattr(currentrequest(), source)
            for k in source_ob.keys():
                l = source_ob.getlist(k)
                if len(l) == 1:
                    data[k] = l[0]
                else:
                    data[k] = l
            return result.replace(
                content = GenshiIter(
                    stream | HTMLFormFiller(name=form_name, id=form_id, data=data),
                    result.content.serializer
                )
            )
        return formfilled
    return formfilled

class GenshiApp(object):
    """
    Return a WSGI application serving genshi templated HTML pages. Example::

        >>> from wsgiref.simple_server import make_server
        >>> render = GenshiRender(TemplateLoader(['path/to/document/root']))
        >>> app = GenshiApp(render)
        >>> print "Serving on port 8000..."
        >>> make_server('', 8000, app).serve_forever()
    """

    def __init__(self, renderer):
        self.renderer = renderer
        (self.document_root,) = renderer.loader.search_path

    def pesto_app(self, request):
        load = self.renderer.loader.load
        path = request.path_info
        template_path = wsgi_normpath(path)
        while template_path and template_path[0] == '/':
            template_path = template_path[1:]

        fs_path = os.path.join(*template_path.split('/'))

        try:
            template = load(fs_path)
        except TemplateNotFound, e:
            if os.path.isdir(os.path.join(self.document_root, fs_path)):
                if template_path != "" and not template_path.endswith('/'):
                    redirect = '/' + template_path + '/'
                    if request.script_name != '':
                        redirect = request.script_name + redirect
                    return Response.redirect(redirect, status=302)
            try:
                template = load(os.path.join(fs_path, 'index.html'))
            except TemplateNotFound:
                return Response.not_found()

        return self.renderer.as_response(template, {})

    __call__ = to_wsgi(pesto_app)

def genshi_app_factory(config, document_root, serializer='xhtml', auto_reload=True):
    """
    Return a WSGI app serving Genshi templated pages from a filesystem
    directory.
    """
    return GenshiApp(
        GenshiRender(
            TemplateLoader([document_root]),
            serializer=serializer
        )
    )

