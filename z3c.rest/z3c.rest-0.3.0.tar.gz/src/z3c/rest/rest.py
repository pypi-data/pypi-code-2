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
"""REST publication and publisher factories

$Id: rest.py 117227 2010-10-05 06:44:05Z icemac $
"""
import cgi
import types
import zope.interface
from z3c.rest import interfaces
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.app.publication.http import HTTPPublication
from zope.publisher.http import HTTPRequest, HTTPResponse
from zope.publisher.interfaces import Redirect


class RESTRequest(HTTPRequest):
    zope.interface.implements(interfaces.IRESTRequest)

    __slots__ = (
        'parameters', # Parameters sent via the query string.
        )

    def __init__(self, body_instream, environ, response=None):
        self.parameters = {}
        super(RESTRequest, self).__init__(body_instream, environ, response)

    def processInputs(self):
        'See IPublisherRequest'
        if 'QUERY_STRING' not in self._environ:
            return
        # Parse the query string into our parameters dictionary.
        self.parameters = cgi.parse_qs(
            self._environ['QUERY_STRING'], keep_blank_values=1)
        # Since the parameter value is always a list (sigh), let's at least
        # detect single values and store them.
        for name, value in self.parameters.items():
            if len(value) == 1:
                self.parameters[name] = value[0]

    def keys(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        d = {}
        d.update(self._environ)
        d.update(self.parameters)
        return d.keys()

    def get(self, key, default=None):
        'See Interface.Common.Mapping.IReadMapping'
        marker = object()
        result = self.parameters.get(key, marker)
        if result is not marker:
            return result

        return super(RESTRequest, self).get(key, default)

    def _createResponse(self):
        return RESTResponse()


class RESTResponse(HTTPResponse):
    zope.interface.implements(interfaces.IRESTResponse)

    errorTemplate = PageTemplateFile("baseerror.pt")

    def handleException(self, exc_info, trusted=False):
        errorClass, error = exc_info[:2]
        if isinstance(errorClass, (types.ClassType, type)):
            if issubclass(errorClass, Redirect):
                self.redirect(error.getLocation(), trusted=trusted)
                return
            title = tname = errorClass.__name__
        else:
            title = tname = unicode(errorClass)

        # Throwing non-protocol-specific exceptions is a good way
        # for apps to control the status code.
        self.setStatus(tname)

        self.setHeader("Content-Type", "text/xml")
        self.setResult(
            self.errorTemplate(name=title, explanation=str(error)))


class RESTView(object):
    zope.interface.implements(interfaces.IRESTView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @apply
    def __parent__():
        def get(self):
            return getattr(self, '_parent', self.context)
        def set(self, parent):
            self._parent = parent
        return property(get, set)


class RESTPublicationRequestFactory(object):
    zope.interface.implements(IPublicationRequestFactory)

    def __init__(self, db):
        """See zope.app.publication.interfaces.IPublicationRequestFactory"""
        self.publication = HTTPPublication(db)

    def __call__(self, input_stream, env, output_stream=None):
        """See zope.app.publication.interfaces.IPublicationRequestFactory"""
        request = RESTRequest(input_stream, env)
        request.setPublication(self.publication)
        return request
