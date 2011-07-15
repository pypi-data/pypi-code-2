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

from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory

from django_hstsmiddleware.patch import patch
from django_hstsmiddleware.middleware import HSTSMiddleware


class HSTSMiddlewareTest(TestCase):
    def setUp(self, *args, **kwargs):
        super(HSTSMiddlewareTest, self).setUp(*args, **kwargs)
        self.middleware = HSTSMiddleware(disable_under_test=False)
        self.factory = RequestFactory()

    def test_request_secure(self):
        request = self.factory.get('/')
        request.is_secure = (lambda: True)
        result = self.middleware.process_request(request)
        self.assertEqual(result, None)

    def test_request_insecure(self):
        request = self.factory.get('/')
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 400, response.content)

    def test_request_disable_under_test(self):
        self.middleware.disable_under_test = True
        request = self.factory.get('/')
        result = self.middleware.process_request(request)
        self.assertEqual(result, None)

    def test_request_disable_under_debug(self):
        with patch(settings, DEBUG=True):
            # When HSTS_DISABLE_UNDER_DEBUG is True, do nothing
            self.middleware.disable_under_debug = True
            request = self.factory.get('/')
            result = self.middleware.process_request(request)
            self.assertEqual(result, None)
            # When HSTS_DISABLE_UNDER_DEBUG is False, operate normally
            self.middleware.disable_under_debug = False
            request = self.factory.get('/')
            response = self.middleware.process_request(request)
            self.assertEqual(response.status_code, 400, response.content)

    def test_request_redirect_to(self):
        url = 'https://testserver/path/'
        self.middleware.redirect_to = url
        request = self.factory.get('/')
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 301, response.content)
        self.assertEqual(response['Location'], url)

    def test_request_bad_request(self):
        request = self.factory.get('/')
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(response.content, '')

    def test_response_max_age(self):
        request = self.factory.get('/')
        response = HttpResponse('')
        self.middleware.max_age = 42
        self.middleware.include_subdomains = False
        self.middleware.process_response(request, response)
        self.assertEqual(response['Strict-Transport-Security'],
                         'max-age=42')

    def test_response_include_subdomains(self):
        request = self.factory.get('/')
        response = HttpResponse('')
        self.middleware.max_age = 42
        self.middleware.include_subdomains = True
        self.middleware.process_response(request, response)
        self.assertEqual(response['Strict-Transport-Security'],
                         'max-age=42 ; includeSubDomains')
