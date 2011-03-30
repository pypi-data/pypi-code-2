# Copyright 2011 Silas Sewell
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json as json_
import htmlentitydefs
import re
import urllib
from xml.sax import saxutils

class objectify(dict):
    """Makes a dictionary behave like an object."""

    def __getattr__(self, name):
        try:
            return objectify(self[name]) if isinstance(self[name], dict) else self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self[name] = value

class json:

    @staticmethod
    def encode(value):
        """JSON-encodes the given Python object."""
        # JSON permits but does not require forward slashes to be escaped.
        # This is useful when json data is emitted in a <script> tag
        # in HTML, as it prevents </script> tags from prematurely terminating
        # the javscript.  Some json libraries do this escaping by default,
        # although python's standard library does not, so we do it here.
        # http://stackoverflow.com/questions/1580647/json-why-are-forward-slashes-escaped
        return json_.dumps(value).replace('</', '<\\/')

    @staticmethod
    def decode(value):
        """Returns Python objects for the given JSON string."""
        return json_.loads(value)

# I originally used the regex from
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
# but it gets all exponential on certain patterns (such as too many trailing
# dots), causing the regex matcher to never return.
# This regex should avoid those problems.
_URL_RE = re.compile(ur"""\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()]|&amp;|&quot;)*(?:[^!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)""")

def linkify(text, shorten=False, extra_params='',
            require_protocol=False, permitted_protocols=['http', 'https']):
    """Converts plain text into HTML with links.

    For example: linkify("Hello http://tornadoweb.org!") would return
    Hello <a href="http://tornadoweb.org">http://tornadoweb.org</a>!

    Parameters:
    shorten: Long urls will be shortened for display.
    extra_params: Extra text to include in the link tag,
        e.g. linkify(text, extra_params='rel="nofollow" class="external"')
    require_protocol: Only linkify urls which include a protocol. If this is
        False, urls such as www.facebook.com will also be linkified.
    permitted_protocols: List (or set) of protocols which should be linkified,
        e.g. linkify(text, permitted_protocols=["http", "ftp", "mailto"]).
        It is very unsafe to include protocols such as "javascript".
    """
    if extra_params:
        extra_params = ' ' + extra_params.strip()

    def make_link(m):
        url = m.group(1)
        proto = m.group(2)
        if require_protocol and not proto:
            return url  # not protocol, no linkify

        if proto and proto not in permitted_protocols:
            return url  # bad protocol, no linkify

        href = m.group(1)
        if not proto:
            href = 'http://' + href   # no proto specified, use http

        params = extra_params

        # clip long urls. max_len is just an approximation
        max_len = 30
        if shorten and len(url) > max_len:
            before_clip = url
            if proto:
                proto_len = len(proto) + 1 + len(m.group(3) or '')  # +1 for :
            else:
                proto_len = 0

            parts = url[proto_len:].split('/')
            if len(parts) > 1:
                # Grab the whole host part plus the first bit of the path
                # The path is usually not that interesting once shortened
                # (no more slug, etc), so it really just provides a little
                # extra indication of shortening.
                url = url[:proto_len] + parts[0] + '/' + \
                        parts[1][:8].split('?')[0].split('.')[0]

            if len(url) > max_len * 1.5:  # still too long
                url = url[:max_len]

            if url != before_clip:
                amp = url.rfind('&')
                # avoid splitting html char entities
                if amp > max_len - 5:
                    url = url[:amp]
                url += '...'

                if len(url) >= len(before_clip):
                    url = before_clip
                else:
                    # full url is visible on mouse-over (for those who don't
                    # have a status bar, such as Safari by default)
                    params += ' title="%s"' % href

        return u'<a href="%s"%s>%s</a>' % (href, params, url)

    # First HTML-escape so that our strings are all safe.
    # The regex is modified to avoid character entites other than &amp; so
    # that we won't pick up &quot;, etc.
    text = utf8.decode(xhtml.escape(text))
    return _URL_RE.sub(make_link, text)

class plus_url:

    @staticmethod
    def escape(value):
        """Returns a valid plus URL-escaped version of the given value."""
        return url.escape(value).replace('%20', '+')

    @staticmethod
    def unescape(value):
        """Un-escapes the given value from a plus encoded URL."""
        return url.unescape(value.replace('+', '%20'))

class query:

    @staticmethod
    def encode(value):
        """Returns a valid URL-encoded version of the given value."""
        return urllib.urlencode([(utf8.encode(n), utf8.encode(v)) for n, v in value.items()])

    @staticmethod
    def decode(value, strict=False, keep_blank_values=False):
        """Decodes a query string from a URL."""
        result = {}
        items = [s2 for s1 in value.split('&') for s2 in s1.split(';')]
        for item in items:
            try:
                k, v = item.split('=', 1)
            except ValueError:
                if strict: raise
                continue
            if v or keep_blank_values:
                k = plus_url.unescape(k)
                v = plus_url.unescape(v)
                if k in result:
                    result[k].append(v)
                else:
                    result[k] = [v]
        return result

def squeeze(value):
    """Replace all sequences of whitespace chars with a single space."""
    return re.sub(r'[\x00-\x20]+', ' ', value).strip()

class url:

    @staticmethod
    def escape(value):
        """Returns a valid URL-escaped version of the given value."""
        return urllib.quote(utf8.encode(value))

    @staticmethod
    def unescape(value):
        """Un-escapes the given value from a URL."""
        return utf8.decode(urllib.unquote(value))

class utf8:

    @staticmethod
    def _unicode_encode(value):
        return value.encode('utf-8')

    @staticmethod
    def _str_decode(value):
        return value.decode('utf-8')

    @staticmethod
    def _dict_encode(value):
        return dict([(utf8.encode(n), utf8.encode(v)) for n, v in value.items()])

    @staticmethod
    def _dict_decode(value):
        return dict([(utf8.decode(n), utf8.decode(v)) for n, v in value.items()])

    @staticmethod
    def _list_encode(value):
        return map(utf8.encode, value)

    @staticmethod
    def _list_decode(value):
        return map(utf8.decode, value)

    @staticmethod
    def encode(value):
        if isinstance(value, unicode):
            return utf8._unicode_encode(value)
        elif isinstance(value, dict):
            return utf8._dict_encode(value)
        elif isinstance(value, (list, tuple)):
            return utf8._list_encode(value)
        else:
            return value

    @staticmethod
    def decode(value):
        if isinstance(value, str):
            return utf8._str_decode(value)
        elif isinstance(value, dict):
            return utf8._dict_decode(value)
        elif isinstance(value, (list, tuple)):
            return utf8._list_decode(value)
        else:
            return value

class xhtml:

    @staticmethod
    def escape(value):
        """Escapes a string so it is valid within XML or XHTML."""
        return utf8.encode(saxutils.escape(value, {'"': '&quot;'}))

    @staticmethod
    def unescape(value):
        """Un-escapes an XML-escaped string."""
        return re.sub(r'&(#?)(\w+?);', _convert_entity, utf8.decode(value))

def _build_unicode_map():
    unicode_map = {}
    for name, value in htmlentitydefs.name2codepoint.iteritems():
        unicode_map[name] = unichr(value)
    return unicode_map

_HTML_UNICODE_MAP = _build_unicode_map()

def _convert_entity(m):
    if m.group(1) == '#':
        try:
            return unichr(int(m.group(2)))
        except ValueError:
            return '&#%s;' % m.group(2)
    try:
        return _HTML_UNICODE_MAP[m.group(2)]
    except KeyError:
        return '&%s;' % m.group(4)
