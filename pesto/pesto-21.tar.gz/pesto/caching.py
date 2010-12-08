# Copyright (c) 2007-2010 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.
"""
pesto.caching
-------------

Utilities to add caching and ETag support.
"""

import time
import re
from datetime import datetime
from cPickle import dumps
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
from functools import wraps

__docformat__ = 'restructuredtext en'

def quoted_string(s):
    r"""
    Return a quoted string, as per RFC 2616 section 2.2

    Synopsis::

        >>> from pesto.caching import quoted_string
        >>> quoted_string(r'"this" is quoted')
        '"\\"this\\" is quoted"'
        >>> quoted_string(r'this is \"quoted\"') == r'"this is \\\"quoted\\\""'
        True
    """
    return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')

START = object()
INSTR = object()
WEAK = object()

def parse_entity_tags(s):
    r"""
    Parse entity tags as found in an If-None-Match header, which may consist of
    multiple comma separated quoted strings, as per RFC 2616 section 3.11

    Example usage::

        >>> from pesto.caching import parse_entity_tags
        >>> parse_entity_tags(r'"tag a", W/"tag b"')
        [(False, 'tag a'), (True, 'tag b')]

        >>> parse_entity_tags(r'"\"a\"", "b"')
        [(False, '"a"'), (False, 'b')]

        >>> parse_entity_tags(r'"\"a\",\\b", "b"')
        [(False, '"a",\\b'), (False, 'b')]

        >>> parse_entity_tags(r'"\"a\",\\b\\", "b"')
        [(False, '"a",\\b\\'), (False, 'b')]

        >>> parse_entity_tags(r'"some longer \"text\"", "b"')
        [(False, 'some longer "text"'), (False, 'b')]
    """
    tokenizer = re.compile(r'''
        (?P<whitespace>\s+) |
        (?P<quotedpair>\\.) |
        (?P<weak>W/) |
        (?P<quote>") |
        (?P<comma>,)
    ''', re.X).finditer

    result = []
    current = ''
    pos = 0
    state = START

    weak = False
    for match in tokenizer(s):

        qdtext = s[pos:match.start()]
        pos = match.end()
        groups = match.groupdict()
        matched = match.group(0)

        if state is START:
            if matched == '"':
                state = INSTR
                weak = False
            if matched == 'W/':
                state = WEAK
                weak = True
            elif groups['comma']:
                result.append((weak, current))
                weak = False
                current = ''

        elif state is WEAK:
            if matched == '"':
                state = INSTR

        elif state is INSTR:
            if groups['quotedpair']:
                current += qdtext + matched[1:]
            elif groups['quote']:
                current += qdtext
                state = START
            else:
                current += qdtext + matched

    result.append((weak, current))
    return result

def make_etag(s, weak=False):
    """
    Return string ``s`` formatted correctly for an ETag header.

    Example usage::

        >>> make_etag('r1089')
        '"r1089"'
        >>> make_etag('r1089', True)
        'W/"r1089"'
    """
    s = s.replace('"', '\\"')
    if weak:
        return 'W/"%s"' % s
    return '"%s"' % s

def with_etag(etag_func, weak=False):
    """
    Decorate the function to add an ETag header to the response object.

    ``etag_funcs`` is a list of functions which will be called with the request
    object as an argument, and return an identifier. This could be a timestamp,
    a revision number, a string, or any other object that identifies the
    revision of the entity.

    Synopsis::

        >>> from pesto.core import to_wsgi
        >>> from pesto.testing import TestApp
        >>> from pesto.response import Response
        >>> from pesto.caching import with_etag
        >>> def generate_etag(request):
        ...     return "whoa nelly!"
        ...
        >>> @with_etag(generate_etag, False)
        ... def view(request):
        ...     return Response(["This response should have an etag"])
        ...
        >>> print TestApp(to_wsgi(view)).get()
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        ETag: "whoa nelly!"\r
        \r
        This response should have an etag

        >>>
    """
    def to_etag(ob):
        """
        Make an etag component from a given object.

            * If the object is a short string, return the string.
            * If the object is numeric, return the string equivalent.
            * If the object is a date or datetime, return the string representation of the number of seconds since the Epoch.
            * Otherwise return the md5 digest of the pickled object
        """
        if isinstance(ob, unicode):
            ob = ob.encode('utf8')
        if isinstance(ob, str) and len(ob) <= 16 and '-' not in ob:
            return ob
        if isinstance(ob, (int, float)):
            return str(ob)
        if isinstance(ob, datetime):
            return time.mktime(ob.utctimetuple())
        return md5(dumps(ob)).hexdigest()

    def with_etag(func):
        """
        Decorate ``func`` to add an ETag head to the return value (which must
        be an instance of ``pesto.response.Response``)
        """

        @wraps(func)
        def with_etag(*args, **kwargs):
            """
            Call ``func`` and add an ETag header to the response
            """
            etag = to_etag(etag_func(*args, **kwargs))
            return func(*args, **kwargs).add_header('ETag', make_etag(etag, weak=weak))

        return with_etag
    return with_etag


def etag_middleware(app):
    """
    Interpret If-None-Match headers and only sends the response on to the
    client if the upstream app doesn't produce a matching etag.

    Note that the upstream application *will* be called on every request.

    The response's content iterator will not be called on cached responses.
    """

    from pesto.response import Response
    from pesto.request import Request

    def call(environ, start_response):
        """
        WSGI middleware callable to handle negotiating caching headers for WSGI
        application ``app``.
        """
        request = Request(environ)
        test_etags = request.get_header('If-None-Match')
        if test_etags is None:
            return app(environ, start_response)

        test_etags = parse_entity_tags(test_etags)

        if environ['REQUEST_METHOD'] not in ('GET', 'HEAD'):
            start_response('412 Precondition Failed', [])
            return []

        allow_weak = not request.get_header('range')

        response = Response.from_wsgi(app, environ, start_response)
        etags = parse_entity_tags(response.get_header('ETag'))
        if etags and etags_match(etags[0], test_etags, allow_weak):
            # NB. If the original content has a .close() method, this will
            # be called by the Response.onclose mechanism, thus giving it a
            # chance to tidy up at the end of the request.
            response = response.replace(
                status='304 Not Modified',
                content=[],
                content_type=None,
            )
        return response(environ, start_response)

    return call

def etags_match(tag, tags, allow_weak=False):
    """
    Return True if any ``tags`` matches an entry in ``tomatch``

    ``tag`` is a tuple of (``weak``, ``entity-tag``)
    ``tags`` is a list of tuples of the same format

    Synopsis::

        # Strong comparison function
        >>> etags_match((False, 'a'), [(False, 'a'), (False, 'b')], allow_weak=False)
        True
        >>> etags_match((False, 'a'), [(True, 'a'), (False, 'b')], allow_weak=False)
        False

        # Weak comparison function
        >>> etags_match((False, 'a'), [(True, 'a'), (False, 'b')], allow_weak=True)
        True

        # Weak comparison function
        >>> etags_match((True, 'b'), [(True, 'a'), (False, 'b')], allow_weak=True)
        True

        # The special case '*' tag
        >>> etags_match((False, 'a'), [(False, '*')])
        True
    """

    if (False, '*') in tags:
        return True

    if allow_weak:
        # Discard weak information
        tags = [(True, t) for w, t in tags]
        tag = (True, tag[1])
    return tag in tags

def no_cache(func):
    """
    Add standard no cache headers to a response::

        >>> from pesto.testing import TestApp
        >>> from pesto.core import to_wsgi
        >>> from pesto.response import Response
        >>> from pesto.caching import no_cache
        >>> @no_cache
        ... def view(request):
        ...     return Response(['cache me if you can!'])
        ...
        >>> print TestApp(to_wsgi(view)).get().text()
        200 OK
        Cache-Control: no-cache, no-store, must-revalidate
        Content-Type: text/html; charset=UTF-8
        Expires: Mon, 26 Jul 1997 05:00:00 GMT
        Pragma: no-store
        <BLANKLINE>
        cache me if you can!
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        """
        Decorated function
        """
        return func(*args, **kwargs).add_headers(
            pragma='no-store',
            cache_control="no-cache, no-store, must-revalidate",
            expires="Mon, 26 Jul 1997 05:00:00 GMT",
        )
    return decorated

