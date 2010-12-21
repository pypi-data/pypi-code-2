# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest
from testStore import TestStore
from utils import file_to_str
from tempfile import mkdtemp
from shutil import rmtree

from stellaris.store import VersionStore
from stellaris.store.exceptions import GraphAlreadyExists
from stellaris.graph import Graph

class TestVersionStore(unittest.TestCase):

    def setUp(self):
        self.tmp_path = mkdtemp()
        config = {'store':{'version_store_path': self.tmp_path}}
        self.store = VersionStore(config)
        
#        self.test_store = Store(config)
#        self.store = StageStore(self.test_store, timeout=5.0)

    def tearDown(self):
        self.store.close()
        rmtree(self.tmp_path)

    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """
        g = Graph('./tests/data/add.rdf', 'test')        
        self.store.create_graph(g)
        self.assertRaises(GraphAlreadyExists, self.store.create_graph, g)
        
    def testRetrieveGraph(self):
        """
        Retrieves a stored graph from the store.
        """
        g1 = Graph('./tests/data/add.rdf', 'test')        
        self.store.create_graph(g1)
        g2 = self.store.retrieve_graph(g1.name)

        self.failUnlessEqual(g2.version, 1)        
        # test if graphs are isomorphic using method from RDFLib
        self.failUnless(g1.graph.isomorphic(g2.graph))

    def testUpdateGraph(self):
        """
        Performs different update operations on a graph.
        """
        g1 = Graph('./tests/data/add.rdf', 'test')        
        self.store.create_graph(g1)
        
        g2 = Graph('./tests/data/update.rdf', 'test2')
        g3 = self.store.update_graph(g1.name, g2)
        self.failUnlessEqual(g3.version, 2)
        
        g4 = self.store.remove_graph(g3.name, g1)
        self.failUnlessEqual(g4.version, 3)

        g5 = self.store.append_graph(g4.name, g1)
        self.failUnlessEqual(g5.version, 4)
          
        # test if graphs are isomorphic using method from RDFLib
        #self.failUnless(g1.graph.isomorphic(g2.graph))

    def testAtomicOps(self):
        """
        Performs multiple operations in a single request.
        """

        final_graph = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:exterms="http://www.example.org/terms/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://www.example.org/index.html">
    <exterms:creation-date>August 16, 1999</exterms:creation-date>
  </rdf:Description>
</rdf:RDF>
"""

        g1 = Graph('./tests/data/add.rdf', 'test')        
        self.store.create_graph(g1)

        g2 = Graph('./tests/data/update.rdf', 'test2')
#        g3 = self.store.update_graph(g1.name, g2)

#        g4 = self.store.remove_from_graph(g3.name, g1)
        g = self.store.graph_atomic_operations('test', [('update', g2),
                                                ('append', g1),
                                                ('remove', g2)])
        
        self.failUnlessEqual(g.version, 2)   
        self.failUnlessEqual(g.graph.serialize(), final_graph)

    def testAtomicOpsFailure(self):
        """
        Performs multiple operations in a single request, makes sure that
        on fails.
        """

        g1 = Graph('./tests/data/add.rdf', 'test')        
        self.store.create_graph(g1)

        g2 = Graph('./tests/data/update.rdf', 'test2')
#        g3 = self.store.update_graph(g1.name, g2)

#        g4 = self.store.remove_from_graph(g3.name, g1)
        try:
            self.store.graph_atomic_operations('test', [('update', g2),
                                                ('append', g1),
                                                ('fail', g2)])
        except AttributeError, e:
            # this is expected
            pass
        
        g = self.store.retrieve_graph('test')
        
        # still version one with the initial content
        self.failUnlessEqual(g.version, 1)
        self.failUnless(g.graph.isomorphic(g1.graph))

    def testExists(self):
        g1 = Graph('./tests/data/add.rdf', '/a/b/c')        
        self.store.create_graph(g1)

        self.failUnlessEqual(self.store.graph_exists('/a/b/c'), '/a/b/c')
        self.failUnlessEqual(self.store.graph_exists('/a/b/c/d'), None)        
        self.failUnlessEqual(self.store.graph_exists('/a/b/c/d', prefix_lookup=True), '/a/b/c')        
        self.failUnlessEqual(self.store.graph_exists('/a/b', prefix_lookup=True), None)
                
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestVersionStore('testCreateGraph'))
#    suite.addTest(TestVersionStore('testRetrieveGraph'))
#    suite.addTest(TestVersionStore('testUpdateGraph'))
#    suite.addTest(TestVersionStore('testAtomicOps'))
#    suite.addTest(TestVersionStore('testAtomicOpsFailure'))
    suite.addTest(TestVersionStore('testExists'))        

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
       
