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
"""REST testing support.

$Id: testing.py 90827 2008-09-04 19:48:01Z mgedmin $
"""
import sys
import zope.interface
from z3c.rest import client, rest, interfaces
from zope.app.publication.http import HTTPPublication
from zope.app.testing.functional import HTTPCaller


class RESTCaller(HTTPCaller):
    """An HTTP caller for REST functional page tests"""

    def chooseRequestClass(self, method, path, environment):
        """Always returns HTTPRequests regardless of methods and content"""
        return rest.RESTRequest, HTTPPublication


class PublisherConnection(object):

    callerFactory = RESTCaller

    def __init__(self, server, port=None):
        self._response = None
        self.server = server
        self.port = port

    def request(self, method, path, body, headers):
        # Extract the handle_error option header
        handleErrorsKey = 'x-zope-handle-errors'
        handleErrors = headers.get(handleErrorsKey, True)
        if handleErrorsKey in headers:
            del headers[handleErrorsKey]

        # Construct the request body and call the publisher
        body = body or ''
        request = ["%s %s HTTP/1.1" % (method, path)]
        for hdr, value in headers.items():
            request.append("%s: %s" % (hdr, value))
        request_string = "\n".join(request) + "\n\n" + body
        self._response = self.callerFactory()(
            request_string, handle_errors=handleErrors)

    def getresponse(self):
        return PublisherResponse(self._response)

    def close(self):
        self._response = None


class SSLPublisherConnection(PublisherConnection):

    def __init__(self, server, port=None):
        print "Using SSL"
        PublisherConnection.__init__(self, server, port=port)


class PublisherResponse(object):
    """Adapter of Zope 3 response objects into httplib.HTTPResponse."""

    def __init__(self, response):
        self._response = response
        self.status = response.getStatus()
        self.reason = response._reason

    def getheaders(self):
        return self._response.getHeaders()

    def read(self):
        return self._response.consumeBody()


class RESTClient(client.RESTClient):
    zope.interface.implements(interfaces.IPublisherRESTClient)

    connectionFactory = PublisherConnection
    sslConnectionFactory = SSLPublisherConnection

    @apply
    def handleErrors():
        """See zope.testbrowser.interfaces.IBrowser"""
        headerKey = 'x-zope-handle-errors'

        def get(self):
            return self.requestHeaders.get(headerKey, True)

        def set(self, value):
            current_value = get(self)
            if current_value == value:
                return
            self.requestHeaders[headerKey] = value

        return property(get, set)
