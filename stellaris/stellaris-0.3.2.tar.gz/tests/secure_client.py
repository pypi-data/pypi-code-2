# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time, os
from tempfile import mkdtemp, mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file, StellarisSecureServerThread as Server
from testWSGIGraphs import TestWSGIGraphs
from benri.client.client import NotFound

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import GraphClient as Client
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

if __name__ == '__main__':
    env_path = mktemp()
    env = Environment(env_path, create=True)

    baseuri = 'https://localhost:9092/'
    graph_col = '/'
    
    bind = 'localhost:9090'

    cert_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'certificates'))
    server_cert_path = os.path.join(cert_base_path, 'localhost_server_cert.pem')
    server_key_path = os.path.join(cert_base_path, 'localhost_server_key.pem')
    cacert_path = os.path.join(cert_base_path, 'CA/cacert.pem')

    user_cert_path = os.path.join(cert_base_path, 'user_cert.pem')
    user_key_path = os.path.join(cert_base_path, 'user_key.pem')

    # this assumes that the server is running on localhost under
    # the path stellaris

    # curl -X GET https://localhost:9092/test --cacert tests/certificates/CA/cacert.pem --cert tests/certificates/user_cert.pem --key tests/certificates/user_key.pem -v

    client = Client('https://%s' % bind , base_path=os.path.join(env_path, '.cache'), prefix=graph_col) #, key=user_key_path, cert=user_cert_path)        

    stat, resp = client.retrieve("hello")
