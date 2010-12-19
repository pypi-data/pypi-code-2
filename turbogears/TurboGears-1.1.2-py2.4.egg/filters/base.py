# -*- coding: UTF-8 -*-
"""Standard TurboGears request filters.

Provides the following filter classes:

``MonkeyDecodingFilter``
    For decoding request data
``NestedvariablesFilter``
    For decoding request variables from dotted notation to nested dicts
``VirtualPathFilter``
    For handling dynamic application roots

"""

__all__ = [
    'MoneyDecodingFilter',
    'NestedVariablesFilter',
    'VirtualPathFilter',
]

import logging

from cherrypy import NotFound, request
from cherrypy.filters.basefilter import BaseFilter

from turbogears import config

from formencode.variabledecode import NestedVariables


log = logging.getLogger('turbogears.filters')


class MonkeyDecodingFilter(BaseFilter):
    """Request filter which decodes the request data according to the encoding
    specified in the request or the encoding set in the configuration.

    The decoding filter is only used if the configuration setting
    ``decoding_filter.on`` is set to ``True``. It defaults to `False``.

    The configuration setting ``decoding_filter.encoding`` can be used to force
    always decoding the request with the given encoding. If this is not set,
    the encoding will be determined from the request headers.

    If neither of the two is specified, the default encoding is used. This can
    be set with the ``decoding_filter.default_encoding`` configuration setting.

    Falls back to UTF-8 decoding or ISO-8859-1 for requests with a main content
    type of "text". Also falls back to ISO-8859-1 if decoding using the
    requested encoding fails.

    """
    @staticmethod
    def decode(from_enc):
        """Recursively decode all values in an iterable from specified encoding.
        """

        def decode_from(value, from_enc):
            if isinstance(value, dict):
                for k, v in value.items():
                    value[k] = decode_from(v, from_enc)
            elif isinstance(value, list):
                newlist = list()
                for item in value:
                    newlist.append(decode_from(item, from_enc))
                value = newlist
            elif isinstance(value, str):
                return value.decode(from_enc)
            return value

        decoded_params = decode_from(request.params, from_enc)
        # This is done in two steps to make sure the exception in
        # before_main can retry a decode with another encoding if needed.
        # DON'T merge those two lines.
        request.params = decoded_params

    def before_main(self):
        """Decode the request data.

        Substituted for CherryPy's decoding filter in
        ``startup.startTurboGears()``.

        See class docstring for details.

        """
        get = config.get
        if not get('decoding_filter.on', False):
            return
        if getattr(request, "_decoding_attempted", False):
            return
        request._decoding_attempted = True
        encoding = get('decoding_filter.encoding', None)
        if not encoding:
            content_type = request.headers.elements("Content-Type")
            if content_type:
                content_type = content_type[0]
                encoding = content_type.params.get("charset", None)
                if not encoding and content_type.value.lower().startswith("text/"):
                    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.1
                    # When no explicit charset parameter is provided by the
                    # sender, media subtypes of the "text" type are defined
                    # to have a default charset value of "ISO-8859-1" when
                    # received via HTTP.
                    encoding = "ISO-8859-1"
            if not encoding:
                encoding = get('decoding_filter.default_encoding', "utf-8")
        try:
            self.decode(encoding)
        except UnicodeDecodeError:
            # IE and Firefox don't supply a charset when submitting form
            # params with a CT of application/x-www-form-urlencoded.
            # So after all our guessing, it could *still* be wrong.
            # Start over with ISO-8859-1, since that seems to be preferred.
            self.decode("ISO-8859-1")


class NestedVariablesFilter(BaseFilter):
    """Request filter that turns request params with names in special dotted
    notation into nested dictionaries via FormEncode's NestedVariables
    validator.

    """
    def before_main(self):
        if hasattr(request, 'params'):
            request.params = NestedVariables.to_python(request.params or {})


class VirtualPathFilter(BaseFilter):
    """Filter that makes CherryPy ignorant of a URL root path.

    That is, you can mount your app so the URI "/users/~rdel/myapp/" maps to
    the root object "/".

    """
    def __init__(self, webpath=''):
        webpath = webpath.rstrip('/')
        if webpath and not webpath.startswith('/'):
             webpath = '/' + webpath
        self.webpath = webpath

    def before_request_body(self):
        """Determine the relevant path info by stripping off prefixes.

        Strips webpath and SCRIPT_NAME from request.object_path and
        sets request.path_info (since CherryPy 2 does not set it).

        """
        webpath = self.webpath
        try:
            webpath += request.wsgi_environ['SCRIPT_NAME'].rstrip('/')
        except (AttributeError, KeyError):
            pass
        if webpath:
            if request.object_path.startswith(webpath):
                request.object_path = request.object_path[len(webpath):] or '/'
            if request.path.startswith(webpath):
                request.path_info = request.path[len(webpath):] or '/'
            else:
                request.path_info = request.path
                # check for webpath only if not forwarded
                try:
                    if not request.wsgi_environ['HTTP_X_FORWARDED_SERVER']:
                        raise KeyError
                except (AttributeError, KeyError):
                    raise NotFound(request.path)
        else:
            request.path_info = request.path
