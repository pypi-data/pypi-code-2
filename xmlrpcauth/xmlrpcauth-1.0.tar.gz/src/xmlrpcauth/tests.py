# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import xmlrpcauth


class TestAuthTransport(unittest.TestCase):

    def test_encoding(self):
        transport = xmlrpcauth.BasicAuthTransport('asdf', 'bsdf')
        host, extra_headers, x509 = transport.get_host_info('localhost')
        self.assertEquals('localhost', host)
        self.assertEquals({'Authorization': 'Basic YXNkZjpic2Rm'}, extra_headers)
        self.assertEquals({}, x509)

    def test_convenience_opener(self):
        xmlrpcauth.Server(
            'http://example.com/foo', 'user', 'password')
        xmlrpcauth.ServerProxy(
            'http://example.com/foo', 'user', 'password')
