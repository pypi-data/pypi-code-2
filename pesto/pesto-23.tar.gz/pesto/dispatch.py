# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
pesto.dispatch
--------------

URL dispatcher WSGI application to map incoming requests to
handler functions.

Example usage::

    >>> from pesto.dispatch import DispatcherApp
    >>>
    >>> dispatcher = DispatcherApp()
    >>> @dispatcher.match('/page/<id:int>', 'GET')
    ... def page(request, id):
    ...     return Response(['You requested page %d' % id])
    ...
    >>> from pesto.testing import TestApp
    >>> TestApp(dispatcher).get('/page/42').body
    'You requested page 42'

"""

__docformat__ = 'restructuredtext en'

__all__ = [
    'DispatcherApp', 'dispatcher_app', 'NamedURLNotFound',
    'URLGenerationError'
]

import re
import types

from logging import getLogger
from urllib import unquote

import pesto
import pesto.core
from pesto.core import PestoWSGIApplication
from pesto.response import Response
from pesto.request import Request, currentrequest
from pesto.wsgiutils import normpath

log = getLogger(__name__)

class URLGenerationError(Exception):
    """
    Error generating the requested URL
    """

class Pattern(object):
    """
    Patterns are testable against URL paths using ``Pattern.test``. If they match,
    they should return a tuple of ``(positional_arguments, keyword_arguments)``
    extracted from the URL path.

    Pattern objects may also be able to take a tuple of
    ``(positional_arguments, keyword_arguments)`` and return a corresponding
    URL path.
    """

    def test(self, url):
        """
        Should return a tuple of ``(positional_arguments, keyword_arguments)`` if the
        pattern matches the given URL path, or None if it does not match.
        """
        raise NotImplementedError

    def pathfor(self, *args, **kwargs):
        """
        The inverse of ``test``: where possible, should generate a URL path for the
        given positional and keyword arguments.
        """
        raise NotImplementedError

class Converter(object):
    """
    Responsible for converting arguments to and from URI components.

    A ``Converter`` class has two instance methods:

        * ``to_string`` - convert from a python object to a string

        * ``from_string`` - convert from URI-encoded bytestring to the target python type.

    It must also define the regular expression pattern that is used to extract
    the string from the URI.
    """


    pattern = '[^/]+'

    def __init__(self, pattern=None):
        """
        Initialize a ``Converter`` instance.
        """
        if pattern is not None:
            self.pattern = pattern

    def to_string(self, ob):
        """
        Convert arbitrary argument ``ob`` to a string representation
        """
        return unicode(ob)

    def from_string(self, s):
        """
        Convert string argument ``a`` to the target object representation, whatever that may be.
        """
        raise NotImplementedError


class IntConverter(Converter):
    """
    Match any integer value and convert to an ``int`` value.
    """

    pattern = r'[+-]?\d+'

    def from_string(self, s):
        """
        Return ``s`` converted to an ``int`` value.
        """
        return int(s)


class UnicodeConverter(Converter):
    """
    Match any string, not including a forward slash, and return a ``unicode`` value
    """

    pattern = r'[^/]+'

    def to_string(self, s):
        """
        Return ``s`` converted to an ``unicode`` object.
        """
        return s

    def from_string(self, s):
        """
        Return ``s`` converted to an ``unicode`` object.
        """
        return unicode(s)

class AnyConverter(UnicodeConverter):
    """
    Match any one of the given string options.
    """

    pattern = r'[+-]?\d+'

    def __init__(self, *args):
        super(AnyConverter, self).__init__(None)
        if len(args) == 0:
            raise ValueError("Must supply at least one argument to any()")
        self.pattern = '|'.join(re.escape(arg) for arg in args)

class PathConverter(UnicodeConverter):
    """
    Match any string, possibly including forward slashes, and return a ``unicode`` object.
    """

    pattern = r'.+'


class ExtensiblePattern(Pattern):
    """
    An extensible URL pattern matcher.

    Synopsis::

        >>> p = ExtensiblePattern(r"/archive/<year:int>/<month:int>/<title:unicode>")
        >>> p.test('/archive/1999/02/blah') == ((), {'year': 1999, 'month': 2, 'title': 'blah'})
        True

    Patterns are split on slashes into components. A component can either be a
    literal part of the path, or a pattern component in the form::

        <identifier> : <regex> : <converter>

    ``identifer`` can be any python name, which will be used as the name of a
    keyword argument to the matched function. If omitted, the argument will be
    passed as a positional arg.

    ``regex`` can be any regular expression pattern. If omitted, the
    converter's default pattern will be used.

    ``converter`` must be the name of a pre-registered converter. Converters
    must support ``to_string`` and ``from_string`` methods and are used to convert
    between URL segments and python objects.

    By default, the following converters are configured:

        * ``int`` - converts to an integer
        * ``path`` - any path (ie can include forward slashes)
        * ``unicode`` - any unicode string (not including forward slashes)
        * ``any`` - a string matching a list of alternatives

    Some examples::

        >>> p = ExtensiblePattern(r"/images/<:path>")
        >>> p.test('/images/thumbnails/02.jpg')
        ((u'thumbnails/02.jpg',), {})

        >>> p = ExtensiblePattern("/<page:any('about', 'help', 'contact')>.html")
        >>> p.test('/about.html')
        ((), {'page': u'about'})

        >>> p = ExtensiblePattern("/entries/<id:int>")
        >>> p.test('/entries/23')
        ((), {'id': 23})


    Others can be added by calling ``ExtensiblePattern.register_converter``
    """

    preset_patterns = (
        ('int', IntConverter),
        ('unicode', UnicodeConverter),
        ('path', PathConverter),
        ('any', AnyConverter),
    )
    pattern_parser = re.compile("""
        <
            (?P<name>\w[\w\d]*)?
            :
            (?P<converter>\w[\w\d]*)
            (?:
                \(
                         (?P<args>.*?)
                \)
            )?
        >
    """, re.X)

    class Segment(object):
        """
        Represent a single segment of a URL, storing information about hte
        ``source``, ``regex`` used to pattern match the segment, ``name`` for
        named parameters and the ``converter`` used to map the value to a URL
        parameter if applicable
        """

        def __init__(self, source, regex, name, converter):
            self.source = source
            self.regex = regex
            self.name = name
            self.converter = converter

    def __init__(self, pattern, name=''):
        """
        Initialize a new ``ExtensiblePattern`` object with pattern ``pattern``
        and an optional name.
        """
        super(ExtensiblePattern, self).__init__()

        self.name = name
        self.preset_patterns = dict(self.__class__.preset_patterns)
        self.pattern = unicode(pattern)

        self.segments = list(self._make_segments(pattern))
        self.args = [ item for item in self.segments if item.converter is not None ]
        self.regex = re.compile(''.join([ segment.regex for segment in self.segments]) + '$')

    def _make_segments(self, s):
        r"""
        Generate successive Segment objects from the given string.

        Each segment object represents a part of the pattern to be matched, and
        comprises ``source``, ``regex``, ``name`` (if a named parameter) and
        ``converter`` (if a parameter)
        """

        for item in split_iter(self.pattern_parser, self.pattern):
            if isinstance(item, unicode):
                yield self.Segment(item, re.escape(item), None, None)
                continue
            groups = item.groupdict()
            name, converter, args = groups['name'], groups['converter'], groups['args']
            if isinstance(name, unicode):
                # Name must be a Python identifiers 
                name = name.encode("ASCII")
            converter = self.preset_patterns[converter]
            if args:
                args, kwargs = self.parseargs(args)
                converter = converter(*args, **kwargs)
            else:
                converter = converter()
            yield self.Segment(item.group(0), '(%s)' % converter.pattern, name, converter)

    def parseargs(self, argstr):
        """
        Return a tuple of ``(args, kwargs)`` parsed out of a string in the format ``arg1, arg2, param=arg3``.

        Synopsis::

            >>> ep =  ExtensiblePattern('')
            >>> ep.parseargs("1, 2, 'buckle my shoe'")
            ((1, 2, 'buckle my shoe'), {})
            >>> ep.parseargs("3, four='knock on the door'")
            ((3,), {'four': 'knock on the door'})

        """
        return eval('(lambda *args, **kwargs: (args, kwargs))(%s)' % argstr)

    def test(self, uri):
        """
        Test ``uri`` and return a tuple of parsed ``(args, kwargs)``, or
        ``None`` if there was no match.
        """
        mo = self.regex.match(uri)
        if not mo:
            return None
        groups = mo.groups()
        assert len(groups) == len(self.args), (
                "Number of regex groups does not match expected count. "
                "Perhaps you have used capturing parentheses somewhere? "
                "The pattern tested was %r." % self.regex.pattern
        )

        try:
            groups = [
                (segment.name, segment.converter.from_string(value))
                  for value, segment in zip(groups, self.args)
            ]
        except ValueError:
            return None

        args = tuple(value for name, value in groups if not name)
        kwargs = dict((name, value) for name, value in groups if name)
        return args, kwargs

    def pathfor(self, *args, **kwargs):
        """
        Example usage::

            >>> p = ExtensiblePattern("/view/<filename:unicode>/<revision:int>")
            >>> p.pathfor(filename='important_document.pdf', revision=299)
            u'/view/important_document.pdf/299'

            >>> p = ExtensiblePattern("/view/<:unicode>/<:int>")
            >>> p.pathfor('important_document.pdf', 299)
            u'/view/important_document.pdf/299'
        """

        args = list(args)
        result = []
        for segment in self.segments:
            if not segment.converter:
                result.append(segment.source)
            elif segment.name:
                try:
                    result.append(segment.converter.to_string(kwargs[segment.name]))
                except IndexError:
                    raise URLGenerationError(
                        "Argument %r not specified for url %r" % (
                            segment.name, self.pattern
                        )
                    )
            else:
                try:
                    result.append(segment.converter.to_string(args.pop(0)))
                except IndexError, e:
                    raise URLGenerationError(
                        "Not enough positional arguments for url %r" % (
                            self.pattern,
                        )
                    )
        return ''.join(result)

    @classmethod
    def register_converter(cls, name, converter):
        """
        Register a preset pattern for later use in URL patterns.

        Example usage::

            >>> from datetime import date
            >>> from time import strptime
            >>> class DateConverter(Converter):
            ...     pattern = r'\d{8}'
            ...     def from_string(self, s):
            ...         return date(*strptime(s, '%d%m%Y')[:3])
            ... 
            >>> ExtensiblePattern.register_converter('date', DateConverter)
            >>> ExtensiblePattern('/<:date>').test('/01011970')
            ((datetime.date(1970, 1, 1),), {})
        """
        cls.preset_patterns += ((name, converter),)

    def __str__(self):
        """
        ``__str__`` method
        """
        return '<%s %r>' % (self.__class__, self.pattern)

class DispatcherApp(object):
    """
    Match URLs to pesto handlers.

    Use the ``match``, ``imatch`` and ``matchre`` methods to associate URL
    patterns and HTTP methods to callables::

        >>> import pesto.dispatch
        >>> from pesto.response import Response
        >>> dispatcher = pesto.dispatch.DispatcherApp()
        >>> def search_form(request):
        ...     return Response(['Search form page'])
        ... 
        >>> def do_search(request):
        ...     return Response(['Search page'])
        ... 
        >>> def faq(request):
        ...     return Response(['FAQ page'])
        ... 
        >>> def faq_category(request):
        ...     return Response(['FAQ category listing'])
        ... 
        >>> dispatcher.match("/search", GET=search_form, POST=do_search)
        >>> dispatcher.match("/faq", GET=faq)
        >>> dispatcher.match("/faq/<category:unicode>", GET=faq_category)

    The last matching pattern wins.

    Patterns can also be named so that they can be retrieved using the urlfor method::

        >>> from pesto.testing import TestApp
        >>> from pesto.request import Request
        >>>
        >>> # URL generation methods require an request object
        >>> request = Request(TestApp.make_environ())
        >>> dispatcher = pesto.dispatch.DispatcherApp()
        >>> dispatcher.matchpattern(
        ...     ExtensiblePattern("/faq/<category:unicode>"), 'faq_category', None, None, GET=faq_category
        ... )
        >>> dispatcher.urlfor('faq_category', request, category='foo')
        'http://localhost/faq/foo'

    Decorated handler functions also grow a ``url`` method that generates valid
    URLs for the function::

        >>> from pesto.testing import TestApp
        >>> request = Request(TestApp.make_environ())
        >>> @dispatcher.match("/faq/<category:unicode>", "GET")
        ... def faq_category(request, category):
        ...     return ['content goes here']
        ... 
        >>> faq_category.url(category='alligator')
        'http://localhost/faq/alligator'

    """

    default_pattern_type = ExtensiblePattern

    def __init__(self, prefix='', cache_size=0, debug=False):
        """
        Create a new DispatcherApp.

        ``prefix``
            A prefix path that will be prepended to all functions mapped via
            ``DispatcherApp.match``

        ``cache_size``
            if non-zero, a least recently used (lru) cache of this size will be
            maintained, mapping URLs to callables.
        """
        self.prefix = prefix
        self.patterns = []
        self.named_patterns = {}
        self.debug = debug
        if cache_size > 0:
            self.gettarget = lru_cached_gettarget(self, self.gettarget, cache_size)

    def status404_application(self, request):
        """
        Return a ``404 Not Found`` response.

        Called when the dispatcher cannot find a matching URI.
        """
        return Response.not_found()

    def status405_application(self, request, valid_methods):
        """
        Return a ``405 Method Not Allowed`` response.

        Called when the dispatcher can find a matching URI, but the HTTP
        methods do not match.
        """

        return Response.method_not_allowed(valid_methods)

    def matchpattern(self, pattern, name, predicate, decorators, *args, **methods):
        """
        Match a URL with the given pattern, specified as an instance of ``Pattern``.

            pattern
                A pattern object, eg ``ExtensiblePattern('/pages/<name:unicode>')``

            name
                A name that can be later used to retrieve the url with ``urlfor``, or ``None``

            predicate
                A callable that is used to decide whether to match this
                pattern, or ``None``. The callable must take a ``Request``
                object as its only parameter and return ``True`` or ``False``.

        Synopsis::

            >>> from pesto.response import Response
            >>> dispatcher = DispatcherApp()
            >>> def view_items(request, tag):
            ...     return Response(["yadda yadda yadda"])
            ...
            >>> dispatcher.matchpattern(
            ...     ExtensiblePattern(
            ...          "/items-by-tag/<tag:unicode>",
            ...     ),
            ...     'view_items',
            ...     None,
            ...     None,
            ...     GET=view_items
            ... )

        URLs can later be generated with the urlfor method on the dispatcher
        object::

            >>> Response.redirect(dispatcher.urlfor(
            ...     'view_items',
            ...     tag='spaghetti',
            ... ))                                      # doctest: +ELLIPSIS
            <pesto.response.Response object at ...>

        Or, if used in the second style as a function decorator, by
        calling the function's ``.url`` method::

            >>> @dispatcher.match('/items-by-tag/<tag:unicode>', 'GET')
            ... def view_items(request, tag):
            ...     return Response(["yadda yadda yadda"])
            ...
            >>> Response.redirect(view_items.url(tag='spaghetti')) # doctest: +ELLIPSIS
            <pesto.response.Response object at ...>

        Note that the ``url`` function can take optional query and fragment
        paraments to help in URL construction::

            >>> from pesto.testing import TestApp
            >>> from pesto.dispatch import DispatcherApp
            >>> from pesto.request import Request
            >>> 
            >>> dispatcher = DispatcherApp()
            >>>
            >>> request = Request(TestApp.make_environ())
            >>> @dispatcher.match('/pasta', 'GET')
            ... def pasta(request):
            ...     return Response(["Tasty spaghetti!"])
            ...
            >>> pasta.url(request, query={'sauce' : 'ragu'}, fragment='eat')
            'http://localhost/pasta?sauce=ragu#eat'
        """

        if not args and not methods:
            # Probably called as a decorator, but no HTTP methods specified
            raise URLGenerationError("HTTP methods not specified")

        if args:
            # Return a function decorator
            def dispatch_decorator(func):
                methods = dict((method, _compose_decorators(func, decorators)) for method in args)
                self.matchpattern(pattern, name, predicate, decorators, **methods)
                _add_url_method(func, self.patterns[-1][0])
                return func
            return dispatch_decorator

        methods = dict(
            (method, _compose_decorators(func, decorators))
            for method, func in methods.items()
        )
        if 'HEAD' not in methods and 'GET' in methods:
            methods['HEAD'] = _make_head_handler(methods['GET'])
        if name:
            self.named_patterns[name] = (pattern, predicate, methods)
        self.patterns.append((pattern, predicate, methods))

    def match(self, pattern, *args, **dispatchers):
        """
        Function decorator to match the given URL to the decorated function,
        using the default pattern type.

        name
            A name that can be later used to retrieve the url with ``urlfor`` (keyword-only argument)

        predicate
            A callable that is used to decide whether to match this pattern.
            The callable must take a ``Request`` object as its only
            parameter and return ``True`` or ``False``. (keyword-only argument)

        decorators
            A list of function decorators that will be applied to the function when
            called as a WSGI application. (keyword-only argument).

            The purpose of this is to allow functions to behave differently
            when called as an API function or as a WSGI application via a dispatcher.
        """
        name = dispatchers.pop('name', None)
        predicate = dispatchers.pop('predicate', None)
        decorators = dispatchers.pop('decorators', [])
        return self.matchpattern(
            self.default_pattern_type(self.prefix + pattern),
            name, predicate, decorators,
            *args, **dispatchers
        )

    def methodsfor(self, path):
        """
        Return a list of acceptable HTTP methods for URI path ``path``.
        """
        methods = {}
        for p, predicate, dispatchers in self.patterns:
            match, params = p.test(path)
            if match:
                for meth in dispatchers:
                    methods[meth] = None

        return methods.keys()

    def urlfor(self, dispatcher_name, request=None, *args, **kwargs):
        """
        Return the URL corresponding to the dispatcher named with ``dispatcher_name``.
        """
        if request is None:
            request = currentrequest()
        if dispatcher_name not in self.named_patterns:
            raise NamedURLNotFound(dispatcher_name)
        pattern, predicate, handlers = self.named_patterns[dispatcher_name]
        try:
            handler = handlers['GET']
        except KeyError:
            handler = handlers.values()[0]
        return request.make_uri(
                path=request.script_name + pattern.pathfor(*args, **kwargs),
                parameters='', query='', fragment=''
        )


    def gettarget(self, path, method, request):
        """
        Generate dispatch targets methods matching the request URI.

        For each function matched, yield a tuple of::

            (function, predicate, positional_args, keyword_args)

        Positional and keyword arguments are parsed from the URI

        Synopsis::

            >>> from pesto.testing import TestApp
            >>> d = DispatcherApp()

            >>> def show_entry(request):
            ...     return [ "Show entry page" ]
            ...
            >>> def new_entry_form(request):
            ...     return [ "New entry form" ]
            ...

            >>> d.match(r'/entries/new',          GET=new_entry_form)
            >>> d.match(r'/entries/<id:unicode>', GET=show_entry)

            >>> request = Request(TestApp.make_environ(PATH_INFO='/entries/foo'))
            >>> list(d.gettarget(u'/entries/foo', 'GET', request))  # doctest: +ELLIPSIS
            [(<function show_entry ...>, None, (), {'id': u'foo'})]

            >>> request = Request(TestApp.make_environ(PATH_INFO='/entries/new'))
            >>> list(d.gettarget(u'/entries/new', 'GET', request)) #doctest: +ELLIPSIS
            [(<function new_entry_form ...>, None, (), {}), (<function show_entry ...>, None, (), {'id': u'new'})]

        """
        request.environ['pesto.dispatcher_app'] = self
        path = normpath(path)
        if self.debug:
            log.debug("gettarget: path is: %r", path)

        return self._gettarget(path, method, request)

    def _gettarget(self, path, method, request):
        """
        Generate ``(func, predicate, positional_args, keyword_args)`` tuples
        """
        if self.debug:
            log.debug("_gettarget: %s %r", method, path)

        for p, predicate, dispatchers in self.patterns:
            result = p.test(path)
            if self.debug:
                log.debug(
                    "_gettarget: %r:%r => %s",
                    str(p),
                    dispatchers,
                    bool(result is not None)
                )
            if result is None:
                continue
            positional_args, keyword_args = result
            if self.debug and method in dispatchers:
                log.debug("_gettarget: matched path to %r", dispatchers[method])
            try:
                target = dispatchers[method]
                if isinstance(target, types.UnboundMethodType):
                    if getattr(target, 'im_self', None) is None:
                        target = getattr(target.im_class(), target.__name__)
                yield target, predicate, positional_args, keyword_args
            except KeyError:
                methods = set(dispatchers.keys())
                request.environ.setdefault(
                    'pesto.dispatcher_app.valid_methods',
                    set()
                ).update(methods)
                if self.debug:
                    log.debug("_gettarget: invalid method for pattern %s: %s", p, method)

        raise StopIteration

    def combine(self, *others):
        """
        Add the patterns from dispatcher ``other`` to this dispatcher.

        Synopsis::

            >>> from pesto.testing import TestApp
            >>> d1 = dispatcher_app()
            >>> d1.match('/foo', GET=lambda request: Response(['d1:foo']))
            >>> d2 = dispatcher_app()
            >>> d2.match('/bar', GET=lambda request: Response(['d2:bar']))
            >>> combined = dispatcher_app().combine(d1, d2)
            >>> TestApp(combined).get('/foo').body
            'd1:foo'
            >>> TestApp(combined).get('/bar').body
            'd2:bar'

        Note settings other than patterns are not carried over from the other
        dispatchers - if you intend to use the debug flag or caching options,
        you must explicitly set them in the combined dispatcher::

            >>> combined = dispatcher_app(debug=True, cache_size=50).combine(d1, d2)
            >>> TestApp(combined).get('/foo').body
            'd1:foo'
        """
        for other in others:
            if not isinstance(other, DispatcherApp):
                raise TypeError("Can only combine with other DispatcherApp")

            self.patterns += other.patterns
        return self

    def __call__(self, environ, start_response):

        request = Request(environ)
        method = request.request_method.upper()
        path = unquote(request.path_info.decode(request.charset))

        if path == u'' or path is None:
            path = u'/'

        for handler, predicate, args, kwargs in self.gettarget(path, method, request):
            if predicate and not predicate(request):
                continue
            environ['wsgiorg.routing_args'] = (args, kwargs)
            return PestoWSGIApplication(handler, *args, **kwargs)(environ, start_response)
        try:
            del environ['wsgiorg.routing_args']
        except KeyError:
            pass

        if 'pesto.dispatcher_app.valid_methods' in environ:
            return self.status405_application(
                request,
                environ['pesto.dispatcher_app.valid_methods']
            )(environ, start_response)
        else:
            return self.status404_application(request)(environ, start_response)

# Alias for backwards compatibility
dispatcher_app = DispatcherApp

def split_iter(pattern, string):
    """
    Generate alternate strings and match objects for all occurances of
    ``pattern`` in ``string``.
    """
    matcher = pattern.finditer(string)
    match = None
    pos = 0
    for match in matcher:
        yield string[pos:match.start()]
        yield match
        pos = match.end()
    yield string[pos:]


class NamedURLNotFound(Exception):
    """
    Raised if the named url can't be found (eg in ``urlfor``).
    """

def lru_cached_gettarget(instance, gettarget, cache_size):
    """
    Wrapper for ``gettarget`` that uses an LRU cache to save path -> dispatcher mappings.
    """
    from repoze.lru import LRUCache
    cache = LRUCache(cache_size)

    def lru_cached_gettarget(path, method, request):
        request.environ['pesto.dispatcher_app'] = instance
        targets = cache.get((path, method))
        if targets is not None:
            return targets

        targets = list(gettarget(path, method, request))
        cache.put((path, method), targets)
        return targets

    return lru_cached_gettarget

def _compose_decorators(func, decorators):
    """
    Return a function that is the composition of ``func`` with all decorators in ``decorators``, eg::

        decorators[-1](decorators[-2]( ... decorators[0](func) ... ))
    """
    if not decorators:
        return func
    for d in reversed(decorators):
        func = d(func)
    return func

def _add_url_method(func, pattern):
    """
    Add a method at ``func.url`` that returns a URL generated from ``pattern``s
    pathfor method.
    """
    def url(request=None, scheme=None, netloc=None, script_name=None, query='', fragment='', *args, **kwargs):
        if request is None:
            request = currentrequest()
        return request.make_uri(
            scheme=scheme,
            netloc=netloc,
            script_name=script_name,
            path_info=pattern.pathfor(*args, **kwargs),
            parameters='',
            query=query,
            fragment=fragment
        )
    try:
        func.url = url
    except AttributeError:
        # Can't set a function attribute on a bound or unbound method
        # http://www.python.org/dev/peps/pep-0232/
        func.im_func.url = url

        return func

def _make_head_handler(handler):
    """
    Take an app that responds to a ``GET`` request and adapt it to one that
    will handle ``HEAD`` requests.
    """

    def head_handler(*args, **kwargs):
        response = handler(*args, **kwargs)
        return response.replace(content = [])
    return head_handler



