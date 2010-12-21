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

class TestFrontendStore(unittest.TestCase):

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
                                 'stand_alone': "false"}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}
        
        self.store = FrontendStore(env)

    def tearDown(self):
        self.store.close()
        rmtree(self.env_path)
        logging.shutdown()

    def testUpDown(self):
        """
        Makes sure setup and teardown works.
        """
        pass
        
    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """
        self.store.create('test', file('./tests/data/add.rdf'))

    def testCreateAndRetrieveGraph(self):
        """
        Creates and then retrieves a graph, ensuring that the contents are 
        correct.
        """
        graph_name = 'test'        
        
        self.store.create(graph_name, file('./tests/data/add.rdf'))

        g_ret = self.store.retrieve(graph_name)
        g_cmp = FileGraph(graph_name, './tests/data/add.rdf')
                
        self.failUnless(g_ret.identical(g_cmp))

    def testDeleteGraph(self):
        """
        Deletes a graph.
        """
        graph_name = 'test'
        self.store.create(graph_name, file('./tests/data/add.rdf'))
        self.store.delete(graph_name)
        self.assertRaises(GraphNotFound, self.store.retrieve, graph_name)        
        

    def testModifyGraph(self):
        """
        Tries the different graph modification operations.
        """
        def modify(op):        
            name = 'test_%s' % op
            self.store.create(name, file('./tests/data/add.rdf'))

            g_stored = self.store.retrieve(name)
            f = getattr(self.store, 'graph_%s' % op)
            g_modified = f(name, file('./tests/data/%s.rdf' % op))
            
            g_updated = self.store.retrieve(name)
            g_cmp = FileGraph(name, './tests/data/add_after_%s.rdf' % op)

            self.failUnlessEqual(g_updated.version, 2)
            self.failUnless(g_updated.identical(g_cmp), msg = 'Graphs are not isomorphic.\nCorrect:\n%s\nFrom store:\n%s' % (g_cmp.serialized, g_updated.serialized))
        
        modify('remove')
        modify('update')
        modify('append')
        modify('replace')                
            
    def testTTL(self):
        """
        Test to set and remove the TTL for a graph.
        """      
        graph_name = 'test'
        self.store.create(graph_name, file('./tests/data/add.rdf'))
        self.store.graph_update_ttl(graph_name, 1.0)
        time.sleep(3.0)
        self.assertRaises(GraphNotFound, self.store.retrieve, graph_name)

    def testQuery(self):
        """
        Execute a query.
        """
        query = """
        PREFIX exterms: <http://www.example.org/terms/>
        SELECT ?date
        WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"""
        
        graph_name = 'test'

        self.store.create(graph_name, file('./tests/data/add.rdf'))        
        res = self.store.query('test', query)
        self.failUnless(res.find("August 16, 1999") > -1)

    def testAtomicOps(self):
        """
        Test the atomic operations.
        """                        
        
        graph_name = 'test'
        self.store.create(graph_name, file('./tests/data/add.rdf'))
        
        self.store.graph_atomic_operations(graph_name, file('./tests/data/atomic_ops.xml'))

        g_new = self.store.retrieve(graph_name)
        g_cmp = FileGraph(graph_name, './tests/data/update.rdf')
        self.failUnlessEqual(g_new.version, 2)
        self.failUnless(g_new.identical(g_cmp))
        self.failUnlessEqual(g_new.uri, self.graph_uri_prefix + graph_name)        
        

    def testExists(self):
        graph_name = 'a/b/c'
        self.store.create(graph_name, file('./tests/data/add.rdf'))
        
        self.failUnlessEqual(self.store.exists('a/b/c'), 'a/b/c')
        self.failUnlessEqual(self.store.exists('a/b/c/d', prefix_lookup=True), 'a/b/c')        
        self.failUnlessRaises(GraphNotFound, self.store.exists, 'a/b', prefix_lookup=True)

    def testRetrieveCollection(self):
        graphs = ['/a/a', '/a/b', '/a/x/a', '/a/x/b', '/b/a']

        for g in graphs:
            self.store.create(g, file('./tests/data/add.rdf'))

        self.failUnlessEqual(self.store.collection_retrieve('/a/'), (['/a/x/'], ['/a/a', '/a/b']))
        self.failUnlessEqual(self.store.collection_retrieve('/'), (['/a/','/b/'], []))

    def testGroups(self):
        """
        Test different group operations.
        """
        name = 'test'
        users = ['a','b','c']
        self.store.group_create(name)
        self.failUnlessRaises(GroupAlreadyExists, self.store.group_create, name)

        self.store.group_update(name, users=users)
        self.failUnlessEqual(self.store.group_retrieve(name), users)
        
        users.append('d')
        self.store.group_update(name, users=users)
        self.failUnlessEqual(self.store.group_retrieve(name), users)
 
        self.store.group_delete(name)
        self.failUnlessRaises(GroupNotFound, self.store.group_retrieve, name)

        groups = {'g1': ['a','b'], 'g2': ['x','y'], 'g3': ['a', 'x']}
        
        for g in groups:
            self.store.group_create(g, users=groups[g])

        correct = groups
        correct['public'] = ['public']
        correct['authenticated'] = ['authenticated']
        correct[ADMIN_GROUP] = [ADMIN_GROUP]
            
        self.failUnlessEqual(self.store.group_list(), correct)
        
    def testGroupsWithCollections(self):
        """
        Tests that groups can be associated and removed from collections.
        """
        # functionality of is_authorized is tested in RDBMSStore
        group_name = 'test'
        users = ['a','b','c']
        self.store.group_create(group_name, users=users)

        graph_name = '/a/b'
        collection_name = '/a/'
        self.store.create(graph_name, file('./tests/data/add.rdf'))
        
        self.store.group_add_to_collection(collection_name, group_name)
        
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'a', access_type=READ), True)
        self.failUnlessRaises(Unauthorized, self.store.is_authorized, graph_name, 'public', access_type=READ_WRITE) 
        
        self.store.group_remove_from_collection(collection_name, group_name)        

    def testAdminGroup(self):
        """
        Tests that the admin group operations work.
        """
        self.failUnlessEqual(self.store.is_admin(ADMIN_GROUP), True)
        self.failUnlessEqual(self.store.is_admin('not_member'), False)        

        users = self.store.group_retrieve(ADMIN_GROUP)
        users.append('test')
        
        self.store.group_update(ADMIN_GROUP, users=users)
        self.failUnlessEqual(self.store.is_admin('test'), True)

    def testGraphURI(self):
        graph_name = '/a/b'
        self.store.create(graph_name, file('./tests/data/add.rdf'))
        g = self.store.retrieve(graph_name)
        self.failUnlessEqual(g.uri, self.graph_uri_prefix + graph_name[1:])
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestFrontendStore('testUpDown'))    
#    suite.addTest(TestFrontendStore('testCreateGraph'))
#    suite.addTest(TestFrontendStore('testCreateAndRetrieveGraph'))
#    suite.addTest(TestFrontendStore('testDeleteGraph'))
#    suite.addTest(TestFrontendStore('testModifyGraph'))
#    suite.addTest(TestFrontendStore('testTTL'))
#    suite.addTest(TestFrontendStore('testQuery'))
#    suite.addTest(TestFrontendStore('testAtomicOps'))
#    suite.addTest(TestFrontendStore('testExists'))
#    suite.addTest(TestFrontendStore('testRetrieveCollection'))    
#    suite.addTest(TestFrontendStore('testGroups'))
#    suite.addTest(TestFrontendStore('testGroupsWithCollections'))
#    suite.addTest(TestFrontendStore('testAdminGroup'))
#    suite.addTest(TestFrontendStore('testGraphURI'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
