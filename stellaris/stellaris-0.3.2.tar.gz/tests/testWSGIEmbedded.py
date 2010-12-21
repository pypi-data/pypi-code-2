# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time, os
from tempfile import mkdtemp, mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file
from testWSGIGraphs import TestWSGIGraphs
from benri.client.client import NotFound

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import GraphClient as Client
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

class TestWSGIEmbedded(TestWSGIGraphs):

    def setUp(self):
        # configure the server to call test_embedded.wsgi in the
        # tests/ directory.
        self.baseuri = 'https://localhost/stellaris/'
        self.graph_col = '/stellaris/'
        
        # get certificate paths
        cert_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'certificates'))
        user_cert_path = os.path.join(cert_base_path, 'user_cert.pem')
        user_key_path = os.path.join(cert_base_path, 'user_key.pem')
        
        self.client = Client(self.baseuri, prefix='/stellaris/', key=user_key_path, cert=user_cert_path)
    
    def tearDown(self):
        pass

    def testCreateGraph(self):
        graph_name = 'test'
        file_name = './tests/data/add.rdf'
        stat, resp = self.graph_op(graph_name, file_name, op='create')
        print stat, resp
        correct_location = urljoin(urljoin(self.baseuri, self.graph_col), graph_name)
        
        self.failUnlessEqual(stat['location'], correct_location)
        # clean up
        self.client.delete(graph_name)

if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestWSGIGraphs('testUpDown'))
    suite.addTest(TestWSGIEmbedded('testCreateGraph'))
#    suite.addTest(TestWSGISecureGraphs('testCreateAndRetrieveGraph'))
#    suite.addTest(TestWSGISecureGraphs('testModifyGraph'))
#    suite.addTest(TestWSGISecureGraphs('testDeleteGraph'))
#    suite.addTest(TestWSGISecureGraphs('testAtomicOps'))
#    suite.addTest(TestWSGISecureGraphs('testExists'))
#    suite.addTest(TestWSGISecureGraphs('testTTL'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()        
