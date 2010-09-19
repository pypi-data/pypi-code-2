# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import pkg_resources
import urllib
import urllib2
import urlparse
import httplib
import socket
import logging

from linkexchange import __version__ as version

default_user_agent = 'LinkExchange/%s (+http://linkexchange.org.ua)' % version

def is_plugin_specifier(x):
    return type(x) in (list, tuple)

def load_plugin(space, specifier):
    specifier = list(specifier)
    name = specifier.pop(0)
    if specifier:
        args = specifier.pop(0)
    else:
        args = []
    if specifier:
        kwargs = specifier.pop(0)
    else:
        kwargs = {}
    cls = pkg_resources.load_entry_point(
            'linkexchange', space, name)
    return cls(*args, **kwargs)

def urlopen_with_timeout(url, timeout):
    class _NonBlockingConnection(httplib.HTTPConnection):
      def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock.settimeout(timeout)
     
    class _NonBlockingHandler(urllib2.HTTPHandler):
      def http_open(self, req):
        return self.do_open(_NonBlockingConnection, req)

    return urllib2.build_opener(_NonBlockingHandler).open(url)

urlopen_errors = (urllib2.URLError, httplib.HTTPException, OSError,
        socket.error)

def normalize_uri(uri):
    if isinstance(uri, unicode):
        uri = uri.encode('utf-8')
    (s, n, p, q, f) = urlparse.urlsplit(uri)
    p = urllib.quote(urllib.unquote(p), '/')
    p = p[:1] + p[1:].rstrip('/')
    return urlparse.urlunsplit((s, n, p, q, f))

def rearrange_blocks(request, blocks, rearrange_map = None):
    """
    Rearranges links blocks according to rearrange_map and depending of request
    URI.

    >>> from linkexchange import PageRequest
    >>> request = PageRequest(host = 'example.com', uri = '/')
    >>> ord('/')
    47
    >>> blocks = [u'b1', u'b2', u'b3']
    >>> rearrange_map = [(0, 2, 0, 3), (2, 3, 3, 5)]
    >>> rearrange_blocks(request, blocks, rearrange_map)
    [u'b2', u'', u'b1', u'', u'b3']
    """
    if rearrange_map is None:
        rearrange_map = [(0, len(blocks), 0, len(blocks))]
    req_sum = sum([ord(x) for x in request.uri])
    result_dic = {}
    result_len = 0
    for i1, i2, o1, o2 in rearrange_map:
        ia = blocks[i1:i2]
        oi = o1 + (req_sum % (o2 - o1))
        while ia:
            if oi not in result_dic:
                result_dic[oi] = ia.pop(0)
            oi += 1
            if oi >= o2:
                oi = o1
        if o2 > result_len:
            result_len = o2
    return [result_dic.get(i, u"") for i in range(0, result_len)]

def parse_rearrange_map(map_str):
    """
    Parse rearrange map string as it specified in the configuration file.

    >>> parse_rearrange_map('0:1-0:3,1:2-3:5,2:3-0:3')
    [(0, 1, 0, 3), (1, 2, 3, 5), (2, 3, 0, 3)]
    """
    def parse_entry(entry):
        entry = entry.strip()
        i, o = entry.split('-')
        i1, i2 = i.split(':')
        o1, o2 = o.split(':')
        return (int(i1), int(i2), int(o1), int(o2))
    try:
        return map(parse_entry, map_str.split(','))
    except ValueError:
        raise ValueError("Invalid rearrange map string")

def configure_logger(handler = None, formatter = None, level = None):
    logger = logging.getLogger('linkexchange')
    if handler is None:
        handler = logging.StreamHandler()
        if formatter is None:
            formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
    try:
        logger.removeHandler(logger._lx_handler)
    except AttributeError:
        pass
    logger.addHandler(handler)
    logger._lx_handler = handler
    if level is not None:
        logger.setLevel(level)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
