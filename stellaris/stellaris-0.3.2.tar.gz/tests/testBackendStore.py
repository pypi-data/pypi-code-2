# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest, time
from tempfile import mkdtemp
from shutil import rmtree

from utils import file_to_str
from stellaris.store import BackendStore
from stellaris.graph import FileGraph

from stellaris.store.exceptions import GraphNotFound

class TestStore(unittest.TestCase):

    def setUp(self):
        self.db_path = mkdtemp()
        
        config = {'db_uri': 'sqlite:///%s' % (self.db_path + '/tmp.db')}        
        config['gc_interval'] = 2.0
        config['log_level'] = 'debug'
        config['log_type'] = 'console'
        
        self.store = BackendStore(config)

    def tearDown(self):
        self.store.close()
        rmtree(self.db_path)

    def testUpDown(self):
        pass

    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """

        self.store.create(FileGraph('test', './tests/data/add.rdf'))

    def testCreateAndRetrieveGraph(self):
        """
        Creates and then retrieves a graph, ensuring that the contents are 
        correct.
        """
        name = 'test'
        g1 = FileGraph(name, './tests/data/add.rdf')
        self.store.create(g1)
        
        g2 = self.store.retrieve('test')
        
        self.failUnless(g1.graph.isomorphic(g2.graph))
        
    def testTTL(self):
        """
        Test to set and remove the TTL for a graph.
        """      
        name = 'test'
        g1 = FileGraph(name, './tests/data/add.rdf')
        self.store.create(g1)
        
        self.store.graph_update_ttl(g1.name, 1.0)
        time.sleep(3.0)
        self.assertRaises(GraphNotFound, self.store.retrieve, g1.name)
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestStore('testUpDown'))
#    suite.addTest(TestStore('testCreateGraph'))
#    suite.addTest(TestStore('testCreateAndRetrieveGraph'))
#    suite.addTest(TestStore('testTTL'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
