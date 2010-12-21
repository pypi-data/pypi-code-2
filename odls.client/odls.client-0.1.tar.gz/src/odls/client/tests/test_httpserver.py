##
## test_httpserver.py
## Login : <uli@pu.smp.net>
## Started on  Wed Aug 11 15:45:36 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Tests to test the testing server.
"""
import doctest
import unittest
import urllib2
from odls.client.http import extended_opener, send_request
from odls.client.tests.testing import ODLSServer, DEFAULT_OPENER, SERVER

def format_response(response):
    response.headers
    headers = str(response.headers)
    body = response.read()
    return "SERVER-RESPONSE:\n%s\n----\n%s" % (headers, body)

class HTTPServerTest(unittest.TestCase):
    def setUp(self):
        self.server = SERVER
        self.server.start()
        self.opener =  DEFAULT_OPENER
        return

    def tearDown(self):
        self.server.stop()
        return

    def test_echo(self):
        result = self.opener.open('http://localhost:8080/echo')
        text = result.read()
        self.assertTrue(
            'Authorization: Digest username="test"' in text)
        self.opener.close()
        req = urllib2.Request('http://localhost:8080/echo', data="a=1")
        response = send_request(self.opener, req)
        result = format_response(response)
        self.opener.close()
        self.assertTrue(
            "{'a': '1'}" in result)
        return

    
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        HTTPServerTest)
    suite.addTest(
        doctest.DocTestSuite(
            optionflags = (
                doctest.NORMALIZE_WHITESPACE
                + doctest.ELLIPSIS
                + doctest.REPORT_NDIFF
                ),
            ),
        )
    return suite

test_suite = suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')
