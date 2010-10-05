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
"""REST publishing interfaces.

$Id: interfaces.py 82249 2007-12-11 00:07:36Z srichter $
"""
import zope.interface
import zope.schema
from zope.location.interfaces import ILocation
from zope.publisher.interfaces import http

class IRESTRequest(http.IHTTPRequest):
    """A special type of request for handling REST-based requests."""

class IRESTResponse(http.IHTTPResponse):
    """A special type of response for handling REST-based requests."""


class IRESTView(ILocation):
    """A REST view"""


class ILink(zope.interface.Interface):
    """An object representing a hyperlink."""

    href = zope.schema.TextLine(
        title=u"URL",
        description=u"The normalized URL of the link",
        required=False)

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the link',
        required=False)

    def click():
        """click the link, going to the URL referenced"""


class IRESTClient(zope.interface.Interface):
    """A REST client.

    This client provides a high-level API to access RESTful Web APIs. The
    interface is designed to resemble the test browser API as much as
    practical.
    """

    connectionFactory = zope.schema.Field(
        title=u"Connection Facotry",
        description=(u'A callable that creates an `httplib`-compliant '
                     u'connection object.'),
        required=True)

    requestHeaders = zope.schema.Dict(
        title=u"Request Headers",
        description=(u"A set of headers that will be sent in every request."),
        required=True)

    url = zope.schema.URI(
        title=u"URL",
        description=(u"The URL the browser is currently showing. It is "
                     u"always a full, absolute URL."),
        required=True)

    headers = zope.schema.List(
        title=u"Response Headers",
        description=(u'A list of all headers that have been returned '
                     u'in the last request.'),
        required=True)

    contents = zope.schema.Text(
        title=u"Contents",
        description=u"The complete response body of the HTTP request.",
        required=True)

    status = zope.schema.Int(
        title=u"Status",
        description=u"The status code of the last response.",
        min=0,
        required=True)

    reason = zope.schema.TextLine(
        title=u"Reason",
        description=u"A short explanation of the status of the last response.",
        required=True)

    fullStatus = zope.schema.TextLine(
        title=u"Full Status",
        description=u"The status code and reason of the last response.",
        required=True)

    def open(url='', data=None, params=None, headers=None, method='GET'):
        """Open a URL and retrieve the result.

        The `url` argument can either be a full URL or a URL relative to the
        previous one. If no URL is specified, then the previous URL will be
        used.

        The `data` is the contents of the request body. It is used to send
        information to the server.

        The `params` describe additional query parameters that will be added
        to the request. Query string parameters are frequently used by RESTive
        APIs to provide additional return value options.

        The `headers` specify additional request headers that are specific for
        this particular request.

        The `method` specifies the HTTP method or verb to use to access the
        resource on the server. While there are only a few methods in RFC
        2616, an string is allowed, since any particular API can extend the
        set of allowed methods.
        """

    def get(url='', params=None, headers=None):
        """Make a GET request to the server.

        For argument details see ``open()``.
        """

    def put(url='', data='', params=None, headers=None):
        """Make a PUT request to the server.

        For argument details see ``open()``.
        """

    def post(url='', data='', params=None, headers=None):
        """Make a POST request to the server.

        For argument details see ``open()``.
        """

    def delete(url='', params=None, headers=None):
        """Make a DELETE request to the server.

        For argument details see ``open()``.
        """

    def setCredentials(username, password):
        """Set the credentials.

        This method adds the necessary information to authenticate the user. A
        common example is basic auth, which inserts the `Authentication`
        request header.
        """

    def goBack(count=1):
        """Go back in history by a certain amount of visisted pages.

        The ``count`` argument specifies how far to go back. It is set to 1 by
        default.
        """

    def reload():
        """Reload the current resource.

        All arguments, including the HTTP method, parameters and additional
        headers are honored.
        """

    def getLink(title=None, url=None, index=0):
        """Return an ILink of the found link.

        This method assumes that the current content type of the response body
        is XML.

        The link is found by the arguments of the method.  Only one can be
        used at a time:

          o ``title`` -- The title or a sub-string thereof of the link.

          o ``url`` -- The URL the link is going to.

        If multiple matching links are found, the `index` specifies which one
        to use.
        """

    def xpath(expr, nsmap=None, single=False):
        """Returns the result of an XPath search expression.

        This method assumes that the current content type of the response body
        is XML.

        The `expr` argument is the actual XPath expression. If the expression
        is incorrect, an unspecified error must be raised.

        The `nsmap` is a mapping from the short version to the full URL of
        each XML namespace used in the expression.

        If `single` is set to ``True``, then only one result is returned,
        instead of a list. If the XPath expression results in more than one
        result, a ``ValueError`` must be raised.
        """


class IPublisherRESTClient(IRESTClient):
    """An extension to the REST client to support test-specific features."""

    handleErrors = zope.schema.Bool(
        title=u"Handle Errors",
        description=(u"Describes whether server-side errors will be handled "
                     u"by the publisher. If set to ``False``, the error will "
                     u"progress all the way to the test, which is good for "
                     u"debugging."),
        default=True,
        required=True)
