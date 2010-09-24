# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import xmlrpclib
import urllib


class BasicAuthTransportBase:

    user = None
    password = None

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def get_host_info(self, host):
        host, extra_headers, x509 = xmlrpclib.Transport.get_host_info(self, host)
        if self.user:
            if extra_headers is None:
                extra_headers = {}
            auth = '%s:%s' % (self.user, self.password)
            auth = auth.encode('base64').strip()
            extra_headers['Authorization'] = 'Basic %s' % auth
        return host, extra_headers, x509


class BasicAuthTransport(BasicAuthTransportBase, xmlrpclib.Transport):
    pass


class SafeBasicAuthTransport(BasicAuthTransportBase, xmlrpclib.SafeTransport):
    pass


def ServerProxy(uri, user, password):
    type, _ = urllib.splittype(uri)
    if type == 'https':
        transport = SafeBasicAuthTransport
    elif type == 'http':
        transport = BasicAuthTransport
    else:
        import pdb; pdb.set_trace() 
        raise IOError('unsupported XML-RPC protocol')
    transport = transport(user, password)
    return xmlrpclib.Server(uri, transport=transport)


Server = ServerProxy
