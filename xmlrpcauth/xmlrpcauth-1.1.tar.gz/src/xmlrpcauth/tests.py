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
        xmlrpcauth.ServerProxy(
            'https://example.com/foo', 'user', 'password')

    def test_choose_safe_transport_on_ssl(self):
        server = xmlrpcauth.Server(
            'https://example.com/foo', 'user', 'password')
        self.assert_(isinstance(server._ServerProxy__transport,
                                xmlrpcauth.SafeBasicAuthTransport))

    def test_choose_normal_transport_without_ssl(self):
        server = xmlrpcauth.Server(
            'http://example.com/foo', 'user', 'password')
        self.assert_(isinstance(server._ServerProxy__transport,
                                xmlrpcauth.BasicAuthTransport))

