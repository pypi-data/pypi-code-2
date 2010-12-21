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

class TestWSGISecureGraphs(TestWSGIGraphs):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'https://localhost:9092/'
        self.graph_col = '/test_graphs/'
        
        self.bind = 'localhost:9092'

        # get certificate paths
        cert_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'certificates'))
        server_cert_path = os.path.join(cert_base_path, 'localhost_server_cert.pem')
        server_key_path = os.path.join(cert_base_path, 'localhost_server_key.pem')
        cacert_path = os.path.join(cert_base_path, 'CA/cacert.pem')

        user_cert_path = os.path.join(cert_base_path, 'user_cert.pem')
        user_key_path = os.path.join(cert_base_path, 'user_key.pem')
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                              'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind,
                                'ssl_key_path': server_key_path,
                                'ssl_cert_path': server_cert_path,
                                'ssl_cacert_path': cacert_path}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'prefix': self.graph_col,
                                 'stand_alone': 'true'}
        env.config['security'] = {'enabled': 'true',
                              'data_path': os.path.join(env.db_dir, 'security')}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}

        self.client = Client('https://%s' % self.bind , base_path=os.path.join(self.env_path, '.cache'), prefix=self.graph_col, key=user_key_path, cert=user_cert_path)

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
        rmtree(self.env_path)
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestWSGIGraphs('testUpDown'))
    suite.addTest(TestWSGISecureGraphs('testCreateGraph'))
    suite.addTest(TestWSGISecureGraphs('testCreateAndRetrieveGraph'))
    suite.addTest(TestWSGISecureGraphs('testModifyGraph'))
    suite.addTest(TestWSGISecureGraphs('testDeleteGraph'))
    suite.addTest(TestWSGISecureGraphs('testAtomicOps'))
    suite.addTest(TestWSGISecureGraphs('testExists'))
    suite.addTest(TestWSGISecureGraphs('testTTL'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()        

