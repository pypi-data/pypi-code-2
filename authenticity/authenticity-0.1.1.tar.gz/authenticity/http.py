# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
HTTP request and response definitions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['Request', 'Response', 'decode_uri', 'encode_uri']

import urlparse

from mod_python import apache


class Request(object):
    """
    Represents an HTTP Request and carries some of the information associated
    with it.
    """
    def __init__(self, method, uri, query, fragment, hostname, secure, client):
        """
        Initialize the HTTP request with the specified values.
        """
        self.method = method
        self.uri = uri
        self.query = query
        self.fragment = fragment
        self.hostname = hostname
        self.secure = secure
        self.client = client

    @classmethod
    def from_apache_request(cls, request, server_path):
        """
        Returns an HTTP request initialized from the specified Apache request.
        """
        if request.method == b'POST':
            query = dict((name.decode('utf-8'), [value.decode('utf-8') for value in values]) \
                         for name, values in urlparse.parse_qs(request.read(), True).iteritems())
        else:
            query = dict((name.decode('utf-8'), [value.decode('utf-8') for value in values]) \
                         for name, values in urlparse.parse_qs(request.args or '', True).iteritems())
        request_uri = request.uri.decode('utf-8')
        if not request_uri.startswith(server_path):
            raise ValueError('Request URI (%s) does not start with server path (%s)' % (request_uri, server_path))
        fragment = request.parsed_uri[apache.URI_FRAGMENT]
        return cls(request.method.decode('ascii'),
                   request_uri[len(server_path):],
                   query,
                   fragment.decode('utf-8') if fragment else None,
                   request.hostname.decode('idna'),
                   request.is_https(),
                   (request.connection.remote_addr[0].decode('ascii'), request.connection.remote_addr[1]))


class Response(object):
    """
    Represents an HTTP response and carries the information required to build
    the response.
    """
    def __init__(self, status, headers=None, content_type=None, body=''):
        """
        Initializes an HTTP response with the specified values.
        """
        self.status = status
        self.headers = headers or {}
        self.content_type = content_type
        self.body = body

    @property
    def body(self):
        """
        The body of the HTTP response.
        """
        return self.__dict__['body']

    @body.setter
    def body(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif not isinstance(value, str):
            value = str(value)
        self.__dict__['body'] = value

    @property
    def content_length(self):
        """
        The length of the HTTP response body.
        """
        return len(self.body)

    def to_apache_response(self, request):
        """
        Sends a reply to the specified Apache request using this response.
        """
        request.status = self.status
        headers = request.headers_out if request.status==apache.HTTP_OK else request.err_headers_out
        for header, values in self.headers.iteritems():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                headers.add(header.encode('ascii'), value.encode('ascii'))
        request.no_cache = True
        request.set_content_length(self.content_length)
        if self.content_length:
            request.content_type = self.content_type.encode('ascii')
            request.write(self.body)


def decode_uri(uri, encoding='utf-8'):
    """
    Decode a sequency of bytes containing a URI where everything except for the
    hostname is encoded using the specified encoding. The hostname is always
    decoded using the IDNA encoding.
    """
    parts = urlparse.urlsplit(uri)
    return urlparse.urlunsplit((parts.scheme.decode('ascii'),
                                '%s:%d' % (parts.hostname.decode('idna'), parts.port) if parts.port else parts.hostname.decode('idna'),
                                parts.path.decode(encoding),
                                parts.query.encode(encoding),
                                parts.fragment.encode(encoding)))


def encode_uri(uri, encoding='utf-8'):
    """
    Encode a unicode containing a URI using the specified encoding for
    everything except the hostname. The hostname is always encoded using the
    IDNA encoding.
    """
    parts = urlparse.urlsplit(uri)
    return urlparse.urlunsplit((parts.scheme.encode('ascii'),
                                b'%s:%d' % (parts.hostname.encode('idna'), parts.port) if parts.port else parts.hostname.encode('idna'),
                                parts.path.encode(encoding),
                                parts.query.encode(encoding),
                                parts.fragment.encode(encoding)))


