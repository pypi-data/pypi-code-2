# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
OpenID request processing.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['OpenIDResponse']

from authenticity.http import Response


class OpenIDResponse(Response):
    """
    An HTTP response which follows the OpenID protocol.
    """
    def __init__(self, server, response):
        """
        Initializes an HTTP response using data from the specified
        OpenIDResponse handled by the OpenID server. Can raise EncodingError.
        """
        webresponse = server.encodeResponse(response)
        headers = dict((name.decode('ascii'), [value.decode('ascii')]) for name, value in webresponse.headers.iteritems())
        super(OpenIDResponse, self).__init__(webresponse.code,
                                             headers=headers,
                                             content_type='text/plain;charset=UTF-8',
                                             body=webresponse.body)
        self.openid_response = response


