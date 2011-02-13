# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Checker implementation for the HTTP family."""

from gocept.lms.interfaces import STATE_OK, STATE_UNAVAILABLE, STATE_TEMPORARY
import gocept.lms.filter
import gocept.lms.interfaces
import grok
import httplib
import logging
import socket
import urllib
import urllib2
import urlparse

log = logging.getLogger(__name__)


http_opener = urllib2.OpenerDirector()
for handler in [urllib2.ProxyHandler,
                urllib2.HTTPHandler,
                urllib2.HTTPSHandler,
                urllib2.HTTPDefaultErrorHandler,
                urllib2.HTTPRedirectHandler,
                urllib2.HTTPErrorProcessor]:
    http_opener.add_handler(handler())


class HTTP(gocept.lms.handler.AbstractURLHandler,
           grok.GlobalUtility):

    grok.name('http')

    def check(self, url):
        request = urllib2.Request(url)
        request.add_header('user-agent', 'Bot/LMS (lms.gocept.com)')
        try:
            connection = http_opener.open(request)
            code = connection.code
        except urllib2.HTTPError, e:
            code = e.code
            reason = e.msg
        except urllib2.URLError, e:
            if isinstance(e.reason, socket.gaierror):
                reason = e.reason.args[1]
            else:
                reason = str(e.reason)
            return STATE_UNAVAILABLE, reason
        except httplib.BadStatusLine:
            return STATE_UNAVAILABLE, 'Presumably, the server closed the '\
                    'connection before sending a valid response.'
        else:
            connection.close()

        log.debug('%s: Got response code %s' % (url, code))
        status, status_msg = code_to_status.get(
            code, (STATE_UNAVAILABLE, 'Invalid response code'))

        if code == 599:
            # Testing support. The 5xx class causes an HTTPError to be  raised.
            status_msg = reason

        return status, status_msg


class HTTPS(HTTP):
    # Derive to register under different name
    grok.name('https')


code_to_status = {
    100: (STATE_OK, 'Continue'),
    101: (STATE_OK, 'Switching Protocols'),

    200: (STATE_OK, 'OK'),
    201: (STATE_OK, 'Created'),
    202: (STATE_OK, 'Accepted'),
    203: (STATE_OK, 'Non-Authoritative Information'),
    204: (STATE_OK, 'No Content'),
    205: (STATE_OK, 'Reset Content'),
    206: (STATE_OK, 'Partial Content'),

    300: (STATE_OK, 'Multiple Choices'),
    301: (STATE_OK, 'Moved Permanently'),
    302: (STATE_OK, 'Found'),
    303: (STATE_OK, 'See Other'),
    304: (STATE_OK, 'Not Modified'),
    305: (STATE_OK, 'Use Proxy'),
    306: (STATE_OK, '(Unused)'),
    307: (STATE_OK, 'Temporary Redirect'),

    400: (STATE_UNAVAILABLE, 'Bad Request'),
    401: (STATE_OK, 'Unauthorized'),
    402: (STATE_UNAVAILABLE, 'Payment required'),
    403: (STATE_UNAVAILABLE, 'Forbidden'),
    404: (STATE_UNAVAILABLE, 'Not Found'),
    405: (STATE_UNAVAILABLE, 'Method Not Allowed'),
    406: (STATE_UNAVAILABLE, 'Not Acceptable'),
    407: (STATE_UNAVAILABLE, 'Proxy Authentication Required'),
    408: (STATE_UNAVAILABLE, 'Request Timeout'),
    409: (STATE_UNAVAILABLE, 'Conflict'),
    410: (STATE_UNAVAILABLE, 'Gone'),
    411: (STATE_UNAVAILABLE, 'Length Required'),
    412: (STATE_UNAVAILABLE, 'Precondition failed'),
    413: (STATE_UNAVAILABLE, 'Request Entity Too Large'),
    414: (STATE_UNAVAILABLE, 'Request-URI Too Long'),
    415: (STATE_UNAVAILABLE, 'Unsupported Media Type'),
    416: (STATE_UNAVAILABLE, 'Request Range Not Satisfiable'),
    417: (STATE_UNAVAILABLE, 'Expectation Failed'),

    500: (STATE_TEMPORARY, 'Internal Server Error'),
    501: (STATE_UNAVAILABLE, 'Not Implemented'),
    502: (STATE_UNAVAILABLE, 'Bad Gateway'),
    503: (STATE_TEMPORARY, 'Service Unavailable'),
    504: (STATE_TEMPORARY, 'Gateway Timeout'),
    505: (STATE_UNAVAILABLE, 'HTTP Version Not Supported'),
    599: (STATE_UNAVAILABLE, 'Used internally by LMS'),
}
