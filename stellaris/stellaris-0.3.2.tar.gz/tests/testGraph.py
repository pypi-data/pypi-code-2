# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest, time
from tempfile import mkdtemp
from shutil import rmtree

from utils import file_to_str
from stellaris.graph import Graph, FileGraph, TYPE_REDLAND, TYPE_RDFLIB

class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph_type = TYPE_RDFLIB
        self.g = Graph('test', file_to_str('./tests/data/add.rdf'), graph_type=self.graph_type)
        
    def testGraphCreate(self):
        pass

    def testIdentical(self):
        g2 = Graph('test', file_to_str('./tests/data/add.rdf'), graph_type=self.graph_type)
        self.failUnlessEqual(self.g.identical(g2), True)

        g3 = Graph('test', file_to_str('./tests/data/update.rdf'), graph_type=self.graph_type)
        self.failUnlessEqual(self.g.identical(g3), False)

#    def testIter(self):
#        for s,p,o in self.g.graph:
#            print s,p,o

    def testFileGraph(self):
        g = FileGraph('test', './tests/data/add.rdf', graph_type=self.graph_type)
        self.failUnless(g.identical(Graph('test', file_to_str('./tests/data/add.rdf'), graph_type=self.graph_type)))

    def testSerialize(self):
        # tricky to test since triples may differ in order
        g = Graph('test', self.g.graph.serialize(), graph_type=self.graph_type)
        self.failUnless(self.g.identical(g))

    def testUpdate(self):
        g2 = Graph('test', file_to_str('./tests/data/update.rdf'), graph_type=self.graph_type)
        self.g.update(g2)
        self.failUnless(self.g.identical(FileGraph('test', './tests/data/add_after_update.rdf', graph_type=self.graph_type)))
        g3 = Graph('test', self.g.serialized, graph_type=self.graph_type)
        self.failUnless(g3.identical(FileGraph('test', './tests/data/add_after_update.rdf', graph_type=self.graph_type)))

    def testAppend(self):
        g2 = Graph('test', file_to_str('./tests/data/append.rdf'), graph_type=self.graph_type)
        self.g.append(g2)
        self.failUnless(self.g.identical(FileGraph('test', './tests/data/add_after_append.rdf', graph_type=self.graph_type)))

    def testRemove(self):
        g2 = Graph('test', file_to_str('./tests/data/remove.rdf'), graph_type=self.graph_type)
        self.g.remove(g2)
        self.failUnless(self.g.identical(FileGraph('test', './tests/data/add_after_remove.rdf', graph_type=self.graph_type)))
        
class TestRedlandGraph(TestGraph):
    def setUp(self):
        self.graph_type = TYPE_REDLAND
        self.g = Graph('test', file_to_str('./tests/data/add.rdf'), graph_type=TYPE_REDLAND)

if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestGraph('testGraphCreate'))
#    suite.addTest(TestGraph('testIter'))
#    suite.addTest(TestGraph('testSerialize'))
#    suite.addTest(TestGraph('testUpdate'))
#    suite.addTest(TestGraph('testAppend'))
#    suite.addTest(TestGraph('testRemove'))
#    suite.addTest(TestGraph('testIdentical'))
#    suite.addTest(TestGraph('testFileGraph'))    

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestGraph)
    unittest.TextTestRunner(verbosity=2).run(suite)

    redland_suite = unittest.TestSuite()
#    redland_suite.addTest(TestRedlandGraph('testGraphCreate'))
#    redland_suite.addTest(TestRedlandGraph('testIter'))
#    redland_suite.addTest(TestRedlandGraph('testSerialize'))
#    redland_suite.addTest(TestRedlandGraph('testUpdate'))
#    redland_suite.addTest(TestRedlandGraph('testAppend'))
#    redland_suite.addTest(TestRedlandGraph('testRemove'))
#    redland_suite.addTest(TestRedlandGraph('testIdentical'))
#    suite.addTest(TestGraph('testFileGraph'))    

#    redland_suite = unittest.TestLoader().loadTestsFromTestCase(TestRedlandGraph)
    unittest.TextTestRunner(verbosity=2).run(redland_suite)

    unittest.main()
