# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests to make sure that everything running behind the 
# WSGI-interface is working properly.

import unittest, time, logging
from tempfile import mktemp
from shutil import rmtree

from utils import file_to_str
from StringIO import StringIO
from urlparse import urljoin

from stellaris.store import FrontendStore
from stellaris.graph import FileGraph
from stellaris.security import READ, READ_WRITE, ADMIN_GROUP
from stellaris.env import Environment

from stellaris.store.exceptions import GraphNotFound, Unauthorized, GroupAlreadyExists, GroupNotFound

from testFrontendStore import TestFrontendStore

class TestFrontendStoreStandalone(TestFrontendStore):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)
        baseuri = 'http://example.org/'
        graphs_prefix = '/test_graphs/'
        
        self.graph_uri_prefix = urljoin(baseuri, graphs_prefix)
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['service'] = {'baseuri': baseuri,
                                 'graphs_prefix': graphs_prefix,
                                 'stand_alone': "true"}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}
        
        self.store = FrontendStore(env)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestFrontendStoreStandalone('testUpDown'))    
    suite.addTest(TestFrontendStoreStandalone('testCreateGraph'))
    suite.addTest(TestFrontendStoreStandalone('testCreateAndRetrieveGraph'))
    suite.addTest(TestFrontendStoreStandalone('testDeleteGraph'))
    suite.addTest(TestFrontendStoreStandalone('testModifyGraph'))
    suite.addTest(TestFrontendStoreStandalone('testTTL'))
    suite.addTest(TestFrontendStoreStandalone('testQuery'))
    suite.addTest(TestFrontendStoreStandalone('testAtomicOps'))
    suite.addTest(TestFrontendStoreStandalone('testExists'))
    suite.addTest(TestFrontendStoreStandalone('testRetrieveCollection'))    
    suite.addTest(TestFrontendStoreStandalone('testGroups'))
    suite.addTest(TestFrontendStoreStandalone('testGroupsWithCollections'))
    suite.addTest(TestFrontendStoreStandalone('testAdminGroup'))
    suite.addTest(TestFrontendStoreStandalone('testGraphURI'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()
