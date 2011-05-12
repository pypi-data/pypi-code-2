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

import urlparse
import Cookie
import os
import os.path

class ClientError(Exception):
    "Generic client error class"

class ClientNetworkError(ClientError):
    "Network error occurred when connecting and retrieving client data"

class ClientDataError(ClientError):
    "Client data parsing/processing error"

class ClientDataAccessError(ClientError):
    "Concurrent data access error"

class PageRequest(object):
    """
    Represents HTTP request.
    """
    def __init__(self, url=None, type=None, host=None, uri=None,
            cookies=None, remote_addr=None, meta=None):
        if url:
            type, host, uri, query, fragment = urlparse.urlsplit(url, 'http')
            if not uri:
                uri = '/'
            if query:
                uri += '?' + query
        self.type = type or 'http'
        self.host = host
        self.uri = uri
        if isinstance(cookies, Cookie.BaseCookie):
            cookies = dict([(k, v.value) for k, v in cookies.items()])
        self.cookies = cookies or {}
        self.remote_addr = remote_addr
        self.meta = meta or {}

    def url(self):
        return '%s://%s%s' % (self.type, self.host, self.uri)

class PageResponse(object):
    """
    Represents HTTP response.
    """
    def __init__(self, status=200, body='', headers=None):
        self.status = status
        self.body = body
        self.headers = headers or {}

class BaseClient(object):
    """
    Base class for link exchange service clients.
    """
    def get_raw_links(self, request):
        """
        Returns list of raw HTML link codes for a given page or special tags if
        no links available.

        @param request: PageRequest object
        @return: list of unicode strings with raw HTML
        """
        return []

    def get_html_links(self, request):
        """
        Returns HTML code with links for given page. The result will be
        formatted according to service features and settings.

        @param request: PageRequest object
        @return: unicode string with HTML
        """
        return u''

    def content_filter(self, request, content):
        """
        Clients that do content filtering implements this method.

        @param request: PageRequest object
        @param content: HTML content (full page or fragment) as unicode string
        @return: filtered content as unicode string
        """
        return content

    def handle_request(self, request):
        """
        Clients that handles HTTP requests implements this method.

        @param request: PageRequest object
        @return: PageResponse object
        """
        return PageResponse(status=404)

    def refresh_db(self, request):
        """
        Force to refresh client database.

        @param request: PageRequest object
        """
