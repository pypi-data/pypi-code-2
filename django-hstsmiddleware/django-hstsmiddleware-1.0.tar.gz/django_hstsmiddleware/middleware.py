# -*- mode: django; coding: utf-8 -*-
#
# Copyright © 2011, TrustCentric
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of TrustCentric nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
django-hstsmiddleware
=====================

Forces the use of `HTTPS` using `HTTP Strict Transport Security` (HSTS).

Strict Transport Security
`````````````````````````

.. _HTTP Strict Transport Security:
   http://tools.ietf.org/html/draft-hodges-strict-transport-sec-02
"""


from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponsePermanentRedirect


class HSTSMiddleware(object):
    """
    Forces the use of `HTTPS`_ using `HTTP Strict Transport Security`_ (HSTS).

    Install it at the top of :data:`settings.MIDDLEWARE_CLASSES`.

    :param int max_age: override :data:`settings.HSTS_MAX_AGE`
    :param bool include_subdomains: override
                                    :data:`settings.HSTS_INCLUDE_SUBDOMAINS`
    :param str redirect_to: override :data:`settings.HSTS_REDIRECT_TO`
    :param bool disable_under_test: don't enforce HTTPS when running unit tests
    :param bool disable_under_debug: don't enforce HTTPS in ``settings.DEBUG``
                                     mode.

    The following Django settings control its default behaviour:

    :data:`settings.HSTS_REDIRECT_TO`:
        Specifies the |URI| to redirect a User Agent to, if it tries
        to use a non-secure connection. Responds with |HTTP Moved
        Permanently|.

        Defaults to ``None``, so no redirect occurs. Instead, responds
        with |HTTP Bad Request|.

    :data:`settings.HSTS_MAX_AGE`:
        The maximum number of seconds that a User Agent will remember
        that this server must be contacted over HTTPS.

        Defaults to ``31536000``, or approximately one year.

    :data:`settings.HSTS_INCLUDE_SUBDOMAINS`:
        If true, tells a User Agent that all subdomains must also be
        contacted over HTTPS, in addition to the current domain.

        Defaults to ``False``
    """

    def __init__(self, max_age=None, include_subdomains=None,
                 redirect_to=None, disable_under_test=True,
                 disable_under_debug=None):
        self.redirect_to = (getattr(settings, 'HSTS_REDIRECT_TO', None)
                            if redirect_to is None
                            else redirect_to)
        self.max_age = (getattr(settings, 'HSTS_MAX_AGE', 31536000)
                        if max_age is None
                        else max_age)
        self.include_subdomains = (getattr(settings, 'HSTS_INCLUDE_SUBDOMAINS',
                                           False)
                                   if include_subdomains is None
                                   else include_subdomains)
        self.disable_under_debug = (getattr(settings,
                                            'HSTS_DISABLE_UNDER_DEBUG',
                                            False)
                                    if disable_under_debug is None
                                    else disable_under_debug)
        # Do not force SSL under Django TestCase, defaults to True
        self.disable_under_test = disable_under_test

    def process_request(self, request):
        """
        Rejects any non-`HTTPS`_ requests with |HTTP Bad Request|.

        If :data:`redirect_to` is not ``None``, any non-HTTPS requests
        get permanently redirected to its value, using |HTTP Moved
        Permanently|. It should be set to an absolute |URI| that is
        served securely.

        When running under the test suite, does nothing, unless
        :data:`disable_under_test` is ``False``.
        """
        if self.disable_under_debug and settings.DEBUG:
            # DEBUG mode, continue processing...
            return None
        if request.is_secure():
            # Secure connection, continue processing...
            return None
        from django.core import mail
        if self.disable_under_test and hasattr(mail, 'outbox'):
            # If django.core.mail.outbox exists, then we must
            # be running under the test suite.
            return None
        if self.redirect_to is not None:
            # Redirect to a secure absolute URL.
            return HttpResponsePermanentRedirect(self.redirect_to)
        return HttpResponseBadRequest()

    def process_response(self, request, response):
        """
        Add the ``Strict-Transport-Security`` header to *response*.

        :param HttpResponse response: `HttpResponse`_

        This header contains :data:`max_age` and
        :data:`include_subdomains`.

        See `HTTP Strict Transport Security`_.
        """
        hsts = 'max-age=%d' % self.max_age
        if self.include_subdomains:
            hsts += ' ; includeSubDomains'
        response['Strict-Transport-Security'] = hsts
        return response
