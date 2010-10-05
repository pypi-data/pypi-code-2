##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""REST Client

$Id: client.py 91201 2008-09-16 22:33:33Z srichter $
"""
import lxml
import lxml.etree
import httplib
import socket
import urllib
import urlparse
import base64
import zope.interface
from z3c.rest import interfaces

def isRelativeURL(url):
    """Determines whether the given URL is a relative path segment."""
    pieces = urlparse.urlparse(url)
    if not pieces[0] and not pieces[1]:
        return True
    return False

def absoluteURL(base, url):
    """Convertes a URL to an absolute URL given a base."""
    if not isRelativeURL(url):
        return url

    pieces = list(urlparse.urlparse(base))
    urlPieces = list(urlparse.urlparse(url))

    if not pieces[2].endswith('/'):
        pieces[2] += '/'
    pieces[2] = urlparse.urljoin(pieces[2], urlPieces[2])

    if urlPieces[4]:
        if pieces[4]:
            pieces[4] = pieces[4] + '&' + urlPieces[4]
        else:
            pieces[4] = urlPieces[4]

    return urlparse.urlunparse(pieces)


def getFullPath(pieces, params):
    """Build a full httplib request path, including a query string."""
    query = ''
    if pieces[4]:
        query = pieces[4]
    if params:
        encParams = urllib.urlencode(params)
        if query:
            query += '&' + encParams
        else:
            query = encParams
    return urlparse.urlunparse(
        ('', '', pieces[2], pieces[3], query, pieces[5]))


class XLink(object):
    """A link implementation for simple XLinks."""
    zope.interface.implements(interfaces.ILink)

    def __init__(self, client, title, url):
        self._client = client
        self.title = title
        self.url = url

    def click(self):
        """See interfaces.ILink"""
        self._client.get(self.url)

    def __repr__(self):
        return '<%s title=%r url=%r>' %(
            self.__class__.__name__, self.title, self.url)


class RESTClient(object):
    zope.interface.implements(interfaces.IRESTClient)

    connectionFactory = httplib.HTTPConnection
    sslConnectionFactory = httplib.HTTPSConnection

    def __init__(self, url=None):
        self.requestHeaders = {}
        self._reset()
        self._history = []
        self._requestData = None
        self.url = ''
        if url:
            self.open(url)

    @property
    def fullStatus(self):
        return '%i %s' %(self.status, self.reason)

    def _reset(self):
        self.headers = []
        self.contents = {}
        self.status = None
        self.reason = None

    def open(self, url='', data=None, params=None, headers=None, method='GET'):
        # Create a correct absolute URL and set it.
        self.url = absoluteURL(self.url, url)

        # Create the full set of request headers
        requestHeaders = self.requestHeaders.copy()
        if headers:
            requestHeaders.update(headers)

        # Let's now reset all response values
        self._reset()

        # Store all the request data
        self._requestData = (url, data, params, headers, method)

        # Make a connection and retrieve the result
        pieces = urlparse.urlparse(self.url)
        if pieces[0] == 'https':
            connection = self.sslConnectionFactory(pieces[1])
        else:
            connection = self.connectionFactory(pieces[1])
        try:
            connection.request(
                method, getFullPath(pieces, params), data, requestHeaders)
            response = connection.getresponse()
        except socket.error, e:
            connection.close()
            self.status, self.reason = e.args
            self._addHistory()
            raise e
        else:
            self.headers = response.getheaders()
            self.contents = response.read()
            self.status = response.status
            self.reason = response.reason
            connection.close()
            self._addHistory()

    def get(self, url='', params=None, headers=None):
        self.open(url, None, params, headers)

    def put(self, url='', data='', params=None, headers=None):
        self.open(url, data, params, headers, 'PUT')

    def post(self, url='', data='', params=None, headers=None):
        self.open(url, data, params, headers, 'POST')

    def delete(self, url='', params=None, headers=None):
        self.open(url, None, params, headers, 'DELETE')

    def setCredentials(self, username, password):
        creds = username + u':' + password
        creds = "Basic " + base64.encodestring(creds.encode('utf-8')).strip()
        self.requestHeaders['Authorization'] = creds

    def _addHistory(self):
        self._history.append((
            self.url, self.requestHeaders, self.headers, self.contents,
            self.status, self.reason, self._requestData
            ))

    def goBack(self, count=1):
        # The user really does not want to go back.
        if count == 0:
            return
        # The user wants to reach before a pre-historical state.
        if len(self._history) < count:
            raise ValueError('There is not enough history.')
        # Let's now get the entry and set the history back to that state.
        entry = self._history[-(count+1)]
        self._history = self._history[:-count]
        # Reset the state.
        (self.url, self.requestHeaders, self.headers, self.contents,
         self.status, self.reason, self._requestData) = entry

    def reload(self):
        self.open(*self._requestData)

    def getLink(self, title=None, url=None, index=0):
        nsmap = {'xlink': "http://www.w3.org/1999/xlink"}
        tree = lxml.etree.fromstring(self.contents)
        res = []
        if title is not None:
            res = tree.xpath(
                '//*[@xlink:title="%s"]' %title, namespaces=nsmap)
        elif url is not None:
            res = tree.xpath(
                '//*[@xlink:href="%s"]' %url, namespaces=nsmap)
        else:
            raise ValueError('You must specify a title or URL.')
        elem = res[index]
        url = elem.attrib.get('{%(xlink)s}href' %nsmap, '')
        return XLink(self,
                     elem.attrib.get('{%(xlink)s}title' %nsmap),
                     absoluteURL(self.url, url))

    def xpath(self, expr, nsmap=None, single=False):
        res = lxml.etree.fromstring(self.contents).xpath(expr, namespaces=nsmap)
        if not single:
            return res
        if len(res) != 1:
            raise ValueError('XPath expression returned more than one result.')
        return res[0]
