# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time, os
from tempfile import mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file, StellarisServerThread as Server
from benri.client.client import NotFound

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import SystemClient, GraphClient
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

class TestWSGISystem(unittest.TestCase):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/test_graphs/'
        
        self.bind = '127.0.0.1:9096'
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'prefix': self.graph_col,
                                 'stand_alone': 'true'}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}
                
        base_path = os.path.join(self.env_path, 'client')
        
        self.graph_client = GraphClient('http://%s' % self.bind, base_path=base_path, prefix=self.graph_col)

        self.system_client = SystemClient('http://%s' % self.bind, base_path=base_path, prefix=self.graph_col)

        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
        rmtree(self.env_path)

    def create_graph(self, name, file_name):
        f = file(file_name, 'r')
        mime, _ = guess_type(file_name)
        stat, resp = self.graph_client.create(name, f, mime)
        f.close()
        return stat, resp
        
    def testUpDown(self):
        pass

    def testCreateGroup(self):
        self.system_client.group_create('test', users=['u1', 'u2'])

    def testRetrieveGroup(self):
        users = ['u1', 'u2']
        self.system_client.group_create('test', users=users)
        self.failUnlessEqual(self.system_client.group_retrieve('test'), users)

    def testDeleteGroup(self):
        self.system_client.group_create('test', users=[])
        self.system_client.group_delete('test')
        
        self.failUnlessRaises(NotFound, self.system_client.group_retrieve, 'test')

    def testUpdateGroup(self):
        users = ['u1', 'u2']
        self.system_client.group_create('test', users=users)
        new_users = self.system_client.group_retrieve('test')
        new_users.append('u3')

        self.system_client.group_update('test', users=new_users)
        self.failUnlessEqual(self.system_client.group_retrieve('test'), new_users)

    def testUpdateCollectionSecurity(self):
        users = ['u1', 'u2']
        self.system_client.group_create('test', users=users)
        self.create_graph('/a/b', './tests/data/add.rdf')
        
        # this only makes sure that no exceptions are thrown, other code ensures
        # the functionality of adding groups to collections
        stat, resp = self.system_client.collection_add_group('/a/', 'test', access_rights='read')
        self.failUnlessEqual(stat['status'], '200', msg='%s\n%s' % (str(stat), resp))
        stat, resp = self.system_client.collection_remove_group('/a/', 'test')
        self.failUnlessEqual(stat['status'], '200', msg='%s\n%s' % (str(stat), resp))        
                
    def testRetrieveGraphAttrs(self):
        graph_name = '/a/b'
        self.create_graph(graph_name, './tests/data/add.rdf')
        attrs = self.system_client.graph_retrieve(graph_name)
        self.failUnless(attrs['ttl'] == None)
        self.failUnlessEqual(attrs['graph-name'], urljoin(self.baseuri, self.graph_col)[:-1] + graph_name)
        self.failUnlessEqual(attrs['version'], 1)

#        self.failUnlessEqual(stat['status'], '200', msg='%s\n%s' % (str(stat), resp))        

    def testUpdateGraphAttrs(self):
        ttl = 2.0
        self.create_graph('/a/b', './tests/data/add.rdf')
        stat, resp = self.system_client.graph_update('/a/b', {'ttl': ttl})
        attrs = self.system_client.graph_retrieve('/a/b')

    def testRetrieveCollection(self):
        graphs = ['/a/a', '/a/b', '/a/x/a', '/a/x/b', '/b/a']
        
        for g in graphs:
            self.create_graph(g, './tests/data/add.rdf')

        self.failUnlessEqual(self.system_client.collection_retrieve('/a/'), (['/a/x/'], ['/a/a', '/a/b']))

        self.failUnlessEqual(self.system_client.collection_retrieve('/'), (['/a/','/b/'], []))        

    def testRetrieveCollectionSpecialChars(self):
        graphs = ['/a/a.b', '/a/c.d/a.b']
        
        for g in graphs:
            self.create_graph(g, './tests/data/add.rdf')

        self.failUnlessEqual(self.system_client.collection_retrieve('/a/'), (['/a/c.d/'], ['/a/a.b']))
        self.failUnlessEqual(self.system_client.collection_retrieve('/a/c.d/'), ([], ['/a/c.d/a.b']))

#        self.failUnlessEqual(self.system_client.collection_retrieve('/'), (['/a/','/b/'], []))        

    def testIndexList(self):
        self.failUnless(['test'], self.system_client.indices())
        
    def testRecoverIndex(self):
        graphs = ['/a/a', '/a/b', '/a/x/a', '/a/x/b', '/b/a']
        
        for g in graphs:
            self.create_graph(g, './tests/data/add.rdf')

        # TODO: fix this test-case        
        self.system_client.recover_index('test')

if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestWSGISystem('testUpDown'))    
#    suite.addTest(TestWSGISystem('testCreateGroup'))
#    suite.addTest(TestWSGISystem('testRetrieveGroup'))
#    suite.addTest(TestWSGISystem('testDeleteGroup'))    
#    suite.addTest(TestWSGISystem('testUpdateGroup'))
#    suite.addTest(TestWSGISystem('testUpdateCollectionSecurity'))
#    suite.addTest(TestWSGISystem('testRetrieveGraphAttrs'))
#    suite.addTest(TestWSGISystem('testUpdateGraphAttrs'))
#    suite.addTest(TestWSGISystem('testRetrieveCollection'))
#    suite.addTest(TestWSGISystem('testRetrieveCollectionSpecialChars'))
#    suite.addTest(TestWSGISystem('testIndexList'))
#    suite.addTest(TestWSGISystem('testRecoverIndex'))    
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestWSGISystem)
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()

