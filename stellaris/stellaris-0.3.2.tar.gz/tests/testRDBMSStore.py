# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest, time
from tempfile import mkdtemp
from shutil import rmtree
from sqlalchemy.orm import clear_mappers

from utils import file_to_str
from stellaris.store.rdbms import RDBMSStore
from stellaris.graph import FileGraph
from stellaris.security import READ, READ_WRITE, ADMIN_READ_WRITE, ADMIN_GROUP, PUBLIC_USER, PUBLIC_GROUP, AUTHENTICATED_GROUP

from stellaris.store.exceptions import GraphNotFound, GroupNotFound, GroupAlreadyExists, Unauthorized, CollectionNotFound

class TestRDBMSStore(unittest.TestCase):

    def setUp(self):
        self.db_path = mkdtemp()
        db_uri = 'sqlite:///%s' % (self.db_path + '/tmp.db')
        
        self.store = RDBMSStore(db_uri, gc_interval=2.0)
        self.store.open()

    def tearDown(self):
        self.store.close()
        clear_mappers()
        rmtree(self.db_path)
        
    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """
        g = FileGraph('test', './tests/data/add.rdf')
        self.store.create(g)

    def testCreateGraphHierarchy(self):
        """
        Creates a graph with different parameters.
        """
        names = ['/a', '/a/b', '/a/b/c', '/a/c', '/b', '/w/x/y/z']
        
        for n in names:
            g = FileGraph(n, './tests/data/add.rdf')
            self.store.create(g)

        self.failUnlessEqual(self.store.collection_exists('/a/'), True)
        self.failUnlessEqual(self.store.collection_exists('/w/x/'), True)

    def testDeleteGraphHierarchy(self):
        """
        Creates a graph with different parameters.
        """
        names = ['/a', '/a/b', '/a/b/c', '/a/c', '/b', '/w/x/y/z']
        
        for n in names:
            g = FileGraph(n, './tests/data/add.rdf')
            self.store.create(g)
                        
        for n in names:
            self.store.delete(n)

        self.failUnlessEqual(self.store.collection_exists('/'), True)
        self.failUnlessRaises(CollectionNotFound, self.store.collection_exists, '/a/')
        self.failUnlessRaises(CollectionNotFound, self.store.collection_exists, '/w/x/')
        self.failUnlessRaises(CollectionNotFound, self.store.collection_exists, '/x/')

    def testCreateAndRetrieveGraph(self):
        """
        Creates and then retrieves a graph, ensuring that the contents are 
        correct.
        """
        name = 'test'
        g = FileGraph(name, './tests/data/add.rdf')
        self.store.create(g)
        
        g_stored = self.store.retrieve(name)
        
        self.failUnless(g_stored.identical(g))

    def testModifyGraph(self):
        """
        Tries the different graph modification operations.
        """
        def modify(op):        
            name = 'test_%s' % op
            g = FileGraph(name, './tests/data/add.rdf', read_only=True)
            self.store.create(g)

            g_stored = self.store.retrieve(name)
            g_remove = FileGraph(name, './tests/data/%s.rdf' % op)
            f = getattr(g_stored, op)
            f(g_remove)
            self.store.update(g_stored)
            
            g_updated = self.store.retrieve(name)
            g_cmp = FileGraph(name, './tests/data/add_after_%s.rdf' % op)
            self.failUnlessEqual(g_updated.version, 2)
            self.failUnless(g_updated.identical(g_cmp), msg = 'Graphs are not identical.\nCorrect:\n%s\nFrom store:\n%s' % (g_cmp.serialized, g_updated.serialized))
        
        modify('remove')
        modify('update')
        modify('append')
        modify('replace')                
        
    def testVersions(self):
        """
        Tests if the versioning of graphs is working.
        """
        name = 'test'
        g = FileGraph(name, './tests/data/add.rdf', read_only=True)
        self.store.create(g)

        g_remove = FileGraph(name, './tests/data/remove.rdf')
        g.remove(g_remove)
        self.store.update(g)
        
        # test retrieving a version that exists
        old_g = self.store.retrieve(name, version=1)
        orig_g = FileGraph(name, './tests/data/add.rdf')
        self.failUnlessEqual(old_g.version, 1)
        self.failUnless(old_g.identical(orig_g))

        # make sure an exception is called when a version that does not
        # exist is accessed
        self.failUnlessRaises(GraphNotFound, self.store.retrieve, name, version=3)

        g_cached = self.store.retrieve(name, cached_version=2)
        # this should return an empty graph
        self.failUnlessEqual(g_cached.serialized, '', msg='Graph not empty, %s' % g_cached.serialized)

        g_cached = self.store.retrieve(name, cached_version=1)
        # this should return the latest version
        self.failUnless(g_cached.identical(g), msg='Graphs are not identical: %s, %s' % (g_cached.serialized, g.serialized))

    def testTTL(self):
        """
        Test to set and remove the TTL for a graph.
        """      
        name = 'test'
        name2 = 'test2'
        g = FileGraph(name, './tests/data/add.rdf', ttl=1.0)
        self.store.create(g)
        # this should be fine
        ret_g = self.store.retrieve(name)

        g = FileGraph(name2, './tests/data/add.rdf')
        self.store.create(g)

        # gc_interval should be 2.0
        time.sleep(3.0)
        
        self.assertRaises(GraphNotFound, self.store.retrieve, name)
        
        g = self.store.retrieve(name2)
        # this graph must still exist
        self.failUnlessEqual(g.version, 1)

        g.ttl = 1.0
        self.store.update(g)
        g = self.store.retrieve(name2)
        
        time.sleep(5.0)
        self.assertRaises(GraphNotFound, self.store.retrieve, name2)
        
    def testExists(self):
        """
        Tests if the graph exists or if any prefix of the graph name exist.
        """

        self.store.create(FileGraph('a/b/c', './tests/data/add.rdf'))
        
        self.failUnlessEqual(self.store.exists('a/b/c'), 'a/b/c')
        self.failUnlessEqual(self.store.exists('a/b/c/d', prefix_lookup=True), 'a/b/c')        
        self.failUnlessRaises(GraphNotFound, self.store.exists, 'a/b', prefix_lookup=True)
        self.failUnlessRaises(GraphNotFound, self.store.exists, '/a/b/c')

        self.store.create(FileGraph('/a/b/c', './tests/data/add.rdf'))
        self.failUnlessEqual(self.store.exists('/a/b/c'), '/a/b/c')
        self.failUnlessEqual(self.store.exists('/a/b/c/d', prefix_lookup=True), '/a/b/c')
        self.failUnlessRaises(GraphNotFound, self.store.exists, '/a/b', prefix_lookup=True)


    def testDelete(self):
        """
        Tests to create and then remove a graph.
        """
        graph_name = 'test'
        self.store.create(FileGraph(graph_name, './tests/data/add.rdf'))
        self.store.delete('test')
        
        self.failUnlessRaises(GraphNotFound, self.store.retrieve, graph_name)
 
    def testAtomicOps(self):
        """
        Tests the atomic operation method of graphs.
        """
        name = 'test'
        self.store.create(FileGraph(name, './tests/data/add.rdf'))
        g = self.store.retrieve(name)
        
        g_update = FileGraph(name, './tests/data/update.rdf')
        g_remove = FileGraph(name, './tests/data/remove.rdf')
        g_append = FileGraph(name, './tests/data/append.rdf')
        
        ops = [('append', FileGraph(name, './tests/data/append.rdf')),
               ('remove', FileGraph(name, './tests/data/remove.rdf')),
               ('update', FileGraph(name, './tests/data/update.rdf'))]
               
        g.atomic_operations(ops)
        self.store.update(g)
        
        g_new = self.store.retrieve(name)
        g_cmp = FileGraph(name, './tests/data/update.rdf')
        self.failUnlessEqual(g_new.version, 2)
        self.failUnless(g_new.identical(g_cmp))

    def testRetrieveCollections(self):
        """
        Tests the retrieve collection method.
        """
        graphs = ['/a/a', '/a/b', '/a/x/a', '/a/x/b']
        
        for g in graphs:
            self.store.create(FileGraph(g, './tests/data/add.rdf'))
        
        a_col = (['/a/x/'], ['/a/a', '/a/b'])
        self.failUnlessEqual(self.store.collection_retrieve('/a/'), a_col)

        x_col = ([], ['/a/x/a', '/a/x/b'])
        self.failUnlessEqual(self.store.collection_retrieve('/a/x/'), x_col)
        
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
        self.failUnlessEqual(self.store.group_list(), groups)
        
    def testGroupsWithCollections(self):
        """
        Tests that groups can be associated and removed from collections.
        """
        group_read = 'read'
        group_read_write = 'read_write'        
        self.store.group_create(group_read, users=['a','b','c'])
        self.store.group_create(group_read_write, users=['x','y','c'])

        graph_name = '/a/b'
        collection_name = '/a/'
        g = FileGraph(graph_name, './tests/data/add.rdf')
        self.store.create(g, user='d')

        # test that the correct exceptions are raised when group and collection is
        # not found
        self.failUnlessRaises(CollectionNotFound, self.store.group_add_to_collection, '/not_there/', group_read)
        self.failUnlessRaises(GroupNotFound, self.store.group_add_to_collection, collection_name, 'no_group')
          
        self.store.group_add_to_collection(collection_name, group_read, access_rights=READ)
        self.store.group_add_to_collection(collection_name, group_read_write, access_rights=READ_WRITE)        

        # test the default policies
        # any user has read access
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'b', access_type=READ), True)
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'h', access_type=READ), True)        

        # test read for the public user 
        self.failUnlessEqual(self.store.is_authorized(graph_name, PUBLIC_USER, access_type=READ), True)        
        # public users does not have write access, but since 'h' is assumed to be authenticated
        # it is allowed to write
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'h', access_type=READ_WRITE), True)

        # try if the public user can write
        self.failUnlessRaises(Unauthorized, self.store.is_authorized, graph_name, PUBLIC_USER, access_type=READ_WRITE)

        # any authenticated user has write access
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'y', access_type=READ_WRITE), True)
        
        # remove the default groups
        self.store.group_remove_from_collection(collection_name, PUBLIC_GROUP)
        self.store.group_remove_from_collection(collection_name, AUTHENTICATED_GROUP)
        
        # test that user from read group has read access and that the users from
        # the read_write group has READ access
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'a', access_type=READ), True)
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'c', access_type=READ), True)
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'x', access_type=READ), True)        

        # test that read user does not have READ_WRITE access
        self.failUnlessRaises(Unauthorized, self.store.is_authorized, graph_name, 'a', access_type=READ_WRITE)
        
        # test that a user in both the READ_WRITE and the READ group have access
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'c', access_type=READ_WRITE), True)

        # user in no group should not have access                
        self.failUnlessRaises(Unauthorized, self.store.is_authorized, graph_name, 'h') 
        
        self.store.group_remove_from_collection(collection_name, group_read)

        # the group is no longer associated with the collection, thus
        # the user should not have access
        self.failUnlessRaises(Unauthorized, self.store.is_authorized, graph_name, 'a') 
    
        # check if the owner is authorized
        self.failUnlessEqual(self.store.is_authorized(graph_name, 'd'), True)

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
                
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestRDBMSStore('testCreateGraph'))
#    suite.addTest(TestRDBMSStore('testCreateGraphHierarchy'))
#    suite.addTest(TestRDBMSStore('testDeleteGraphHierarchy'))
#    suite.addTest(TestRDBMSStore('testCreateAndRetrieveGraph'))
#    suite.addTest(TestRDBMSStore('testModifyGraph'))
#    suite.addTest(TestRDBMSStore('testVersions'))    
#    suite.addTest(TestRDBMSStore('testTTL'))
#    suite.addTest(TestRDBMSStore('testDelete'))    
#    suite.addTest(TestRDBMSStore('testExists'))
#    suite.addTest(TestRDBMSStore('testAtomicOps'))
#    suite.addTest(TestRDBMSStore('testRetrieveCollections'))
#    suite.addTest(TestRDBMSStore('testGroups'))
#    suite.addTest(TestRDBMSStore('testGroupsWithCollections'))
#    suite.addTest(TestRDBMSStore('testAdminGroup'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
