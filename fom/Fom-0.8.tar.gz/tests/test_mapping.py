import uuid
import unittest

from fom.db import PRIMITIVE_CONTENT_TYPE
from fom.api import ItemPermissionsApi
from fom.dev import sandbox_fluid
from fom.mapping import (path_split, path_child, Namespace, Tag, Object,
    tag_relation, tag_value, tag_collection, Policy, Permissions,
    tag_relations)
from fom.errors import Fluid404Error, Fluid412Error, Fluid400Error

class TestPath(unittest.TestCase):

    def test_parent(self):
        self.assertEquals(path_split(u'goo/moo'), [u'goo', u'moo'])

    def test_child(self):
        self.assertEquals(path_child(u'foo', u'blah'), u'foo/blah')

    def test_empty(self):
        self.assertEquals(path_child(u'', 'foo'), u'foo')

class PolicyTest(unittest.TestCase):

    def test_init(self):
        # default
        p = Policy()
        self.assertEquals('open', p.policy)
        self.assertEquals([], p.exceptions)
        # overridden
        p = Policy(policy='closed', exceptions=['foo',])
        self.assertEquals('closed', p.policy)
        self.assertEquals(['foo',], p.exceptions)

    def test_set_policy(self):
        p = Policy(policy='closed')
        # good
        p.policy = 'open'
        self.assertEquals('open', p.policy)
        p.policy = 'closed'
        self.assertEquals('closed', p.policy)

    def test_set_exceptions(self):
        p = Policy(policy='open', exceptions=['foo'])
        # good
        p.exceptions = ['foo', 'bar']
        self.assertEqual(['foo', 'bar'], p.exceptions)
        p.exceptions.append('baz')
        self.assertEqual(['foo', 'bar', 'baz'], p.exceptions)

class PermissionsTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

    def test_init(self):
        p = Permissions(self.fluid.permissions.namespaces['test'])
        self.assertTrue(isinstance(p.api, ItemPermissionsApi))

    def test_get(self):
        p = Permissions(self.fluid.permissions.namespaces['test'])
        # good
        policy = p['create']
        self.assertTrue(isinstance(policy, Policy))
        # bad
        self.assertRaises(Fluid400Error, p.__getitem__, 'foo')

    def test_set(self):
        p = Permissions(self.fluid.permissions.namespaces['test'])
        policy = Policy(policy='closed', exceptions=['test', ])
        # good
        p['create'] = policy
        check_policy = p['create']
        self.assertEquals(policy.policy, check_policy.policy)
        self.assertEquals(policy.exceptions, check_policy.exceptions)
        # bad
        self.assertRaises(Fluid400Error, p.__setitem__, 'foo', policy)
        self.assertRaises(TypeError, p.__setitem__, 'create', 'foo')

class NamespaceTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()
        self.uid = str(uuid.uuid4())
        self.path = u'test/%s' % self.uid

    def test_new(self):
        n = Namespace(u'test')
        self.assertEquals(n.path, u'test')
        self.assertTrue(n.fluid is self.fluid)

    def test_create(self):
        ns = Namespace(self.path)

        ns.create(u'fomtest description')

        childns = ns.create_namespace(u'child', u'fomtest child')
        childns.delete()

        # access the namespace's low-level api
        ns.api.get()
        ns.api.put(u'A better description')
        ns.api.post(u'child', u'fomtest child')

        childNs = Namespace(u'%s/%s' % (self.path, u'child'))
        childNs.delete()

        ns.delete()

    def test_description(self):
        ns = Namespace(self.path)
        ns.create(u'testdesc')
        self.assertEquals(ns.description, u'testdesc')
        ns.description = u'newdesc'
        self.assertEquals(ns.description, u'newdesc')

    def test_create_child(self):
        n = Namespace(u'test')
        child = n.create_namespace(self.uid, u'fomtest description')
        self.assertEquals(child.path, self.path)
        child.delete()

    def test_child_namespace(self):
        n = Namespace(u'test')
        child = n.namespace(u'test')
        self.assertTrue(isinstance(child, Namespace))
        self.assertEquals(child.path, u'test/test')

    def test_child_tag(self):
        n = Namespace(u'test')
        child = n.tag(u'test')
        self.assertTrue(isinstance(child, Tag))
        self.assertEquals(child.path, u'test/test')

    def test_create_delete_child_tag(self):
        n = Namespace(u'test')
        tag_name = str(uuid.uuid4())
        new_tag = n.create_tag(tag_name, 'a test', False)
        self.assertTrue(isinstance(new_tag, Tag))
        new_tag.delete()
        self.assertTrue(tag_name not in n.tag_names)

    def test_permissions(self):
        n = Namespace(u'test')
        # Get good
        p = n.permissions['create']
        self.assertTrue(isinstance(p, Policy))
        # Get bad
        self.assertRaises(Fluid400Error, n.permissions.__getitem__, 'foo')
        child = n.create_namespace(self.uid, u'fomtest description')
        # Put good
        test_policy = Policy(policy="open", exceptions=['fluiddb', ])
        child.permissions['create'] = test_policy
        p = child.permissions['create']
        self.assertEquals('open', p.policy)
        self.assertEquals(['fluiddb'], p.exceptions)
        # Put bad
        self.assertRaises(Fluid400Error, n.permissions.__setitem__, 'foo',
                          test_policy)
        child.delete()

class ObjectTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

    def testNew(self):
        o = Object()
        self.assertTrue(o.uid is None)

    def testCreate(self):
        o = Object()
        o.create()
        self.assert_(o.uid)

    def testGet(self):
        o = Object()
        o.create()
        self.assertRaises(Fluid404Error, o.get, 'test/fomtest')

    def testSetPrimitive(self):
        o = Object()
        o.create()
        self.assertRaises(Fluid404Error, o.get, 'test/fomtest')
        for value in (None, True, False, 123, 45.67, 'hey there'):
            o.set('test/fomtest', value)
            self.assertEqual(o.get('test/fomtest'),
                (value, PRIMITIVE_CONTENT_TYPE))

    def testSetOpaque(self):
        o = Object()
        o.create()
        self.assertRaises(Fluid404Error, o.get, 'test/fomtest')
        o.set('test/fomtest', 'xyz', 'application/bananas')
        self.assertEqual(o.get('test/fomtest'), ('xyz', 'application/bananas'))

    def testHas(self):
        o = Object()
        o.create()
        self.assertFalse(o.has('test/fomtest'))
        o.set('test/fomtest', 123)
        self.assertTrue(o.has('test/fomtest'))

    def testTags(self):
        o = Object()
        o.create()
        self.assertEquals(o.tag_paths, [])
        self.assertEquals(o.tags, [])
        o.set('test/fomtest', 123)
        self.assertTrue('test/fomtest' in o.tag_paths)
        self.assertEquals(o.tags[0].path, 'test/fomtest')

    def testFilter(self):
        # the simple good case
        results = Object.filter('fluiddb/users/username = "ntoll"')
        self.assertEquals(1, len(results))
        self.assertEquals(u'Object for the user named ntoll', results[0].about)
        # Lets try creating a class based on Object and use that...
        class UserClass(Object):
            username = tag_value('fluiddb/users/username')
            name = tag_value('fluiddb/users/name')
        users = UserClass.filter('fluiddb/users/username = "ntoll"')
        self.assertEquals(1, len(results))
        user = users[0]
        self.assertEquals(u'Object for the user named ntoll', user.about)
        self.assertEquals(u'ntoll', user.username)
        self.assertEquals(u'ntoll', user.name)
        # Lets try that again but pass in the UserClass to the Object "version"
        users = Object.filter('fluiddb/users/username = "ntoll"', result_type=UserClass)
        self.assertEquals(1, len(results))
        user = users[0]
        self.assertEquals(u'Object for the user named ntoll', user.about)
        self.assertEquals(u'ntoll', user.username)
        self.assertEquals(u'ntoll', user.name)

    def testEquality(self):
        b = Object()
        b.create()
        a = Object(b.uid)
        self.assertEqual(a, b)

class TagValueTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()
        n = Namespace(u'test')
        for name in (u'fomtest', u'fomtest2'):
            try:
                n.create_tag(u'fomtest', u'%s description' % name, False)
            except Fluid412Error:
                pass

    def testDefaultType(self):
        """
        Make sure that the content-type is set to the appropriate mime-type
        should the defaultType argument be specified
        """
        class fomtest(Object):
            ft = tag_value('test/fomtest')
            ft2 = tag_value('test/fomtest2', 'text/html')

        obj = fomtest(about="A test object")
        # default behaviour
        obj.ft = 1
        obj.ft2 = '<html><body>Hello, World</body></html>'
        ft_result = obj.get('test/fomtest')
        ft2_result = obj.get('test/fomtest2')
        self.assertEquals('application/vnd.fluiddb.value+json', ft_result[1])
        self.assertEquals('text/html', ft2_result[1])
        # But we *can* override the mime if we use the object's set method
        obj.set('test/fomtest2', 'foo', None)
        self.assertEquals('foo', obj.ft2)
        ft2_result = obj.get('test/fomtest2')
        self.assertEquals('application/vnd.fluiddb.value+json', ft2_result[1])

    def testSetCaching(self):
        class fomtest(Object):
            ft = tag_value('test/fomtest')
        obj = fomtest(about="A test object")
        obj.ft = 1
        self.assertEquals(obj.get_cached('test/fomtest'), 1)

    def testGetCaching(self):
        class fomtest(Object):
            ft = tag_value('test/fomtest')
        obj = fomtest(about="A test object")
        obj.ft = 1
        obj2 = fomtest(about="A test object")
        self.assertEquals(obj2.get_cached('test/fomtest'), None)
        self.assertEquals(obj2.ft, 1)
        self.assertEquals(obj.get_cached('test/fomtest'), 1)

    def testCacheDeleting(self):
        class fomtest(Object):
            ft = tag_value('test/fomtest')
        obj = fomtest(about="A test object")
        obj.ft = 1
        self.assertEquals(obj.get_cached('test/fomtest'), 1)
        obj.refresh()
        self.assertEquals(obj.get_cached('test/fomtest'), None)

    def testCacheDeletingSingle(self):
        class fomtest(Object):
            ft = tag_value('test/fomtest')
        obj = fomtest(about="A test object")
        obj.ft = 1
        self.assertEquals(obj.get_cached('test/fomtest'), 1)
        obj.refresh('test/fomtest')
        self.assertEquals(obj.get_cached('test/fomtest'), None)

    def testCacheEntireFlow(self):
        class fomtest(Object):
            ft = tag_value('test/fomtest')
        obj = fomtest(about="A test object")
        obj.ft = 1
        obj2 = fomtest(about="A test object")
        self.assertEquals(obj2.ft, obj.ft)
        self.assertEquals(obj.get_cached('test/fomtest'), 1)
        self.assertEquals(obj2.get_cached('test/fomtest'), 1)
        obj.ft = 2
        self.assertEquals(obj2.get_cached('test/fomtest'), 1)
        obj2.refresh('test/fomtest')
        self.assertEquals(obj2.ft, 2)
        self.assertEquals(obj2.ft, obj.ft)


class TagTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

    def testNew(self):
        t = Tag('test/fomtest')
        self.assertEquals(t.path, 'test/fomtest')

    def testGetDescription(self):
        t = Tag('test/fomtest')
        t.description = u'banana'
        self.assertEquals(t.description, u'banana')

    def testSetDescription(self):
        t = Tag('test/fomtest')
        t.description = u'melon'
        self.assertEquals(t.description, u'melon')

    def test_permissions(self):
        t = Tag('test/fomtest')
        # Get good
        p = t.permissions['update']
        self.assertTrue(isinstance(p, Policy))
        # Get bad
        self.assertRaises(Fluid400Error, t.permissions.__getitem__, 'foo')
        # Put good
        test_policy = Policy(policy="open", exceptions=['fluiddb', ])
        t.permissions['update'] = test_policy
        p = t.permissions['update']
        self.assertEquals('open', p.policy)
        self.assertEquals(['fluiddb'], p.exceptions)
        # Put bad
        self.assertRaises(Fluid400Error, t.permissions.__setitem__, 'foo',
                          test_policy)

    def test_value_permissions(self):
        t = Tag('test/fomtest')
        # Get good
        p = t.value_permissions['see']
        self.assertTrue(isinstance(p, Policy))
        # Get bad
        self.assertRaises(Fluid400Error, t.value_permissions.__getitem__, 'foo')
        # Put good
        test_policy = Policy(policy="open", exceptions=['fluiddb', ])
        t.value_permissions['see'] = test_policy 
        p = t.value_permissions['see']
        self.assertEquals('open', p.policy)
        self.assertEquals(['fluiddb'], p.exceptions)
        # Put bad
        self.assertRaises(Fluid400Error, t.value_permissions.__setitem__,
                          'foo', test_policy)

class RelationTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

        n = Namespace(u'test')
        for name in (u'fomtest', u'fomtest2'):
            try:
                n.create_tag(u'fomtest', u'%s description' % name, False)
            except Fluid412Error:
                pass

        class A(Object):
            fomtest = tag_relation(u'test/fomtest')
            fomtest2 = tag_value(u'test/fomtest2')

        self.A = A

    def testRelation(self):
        a1 = self.A()
        a1.create()

        a2 = self.A()
        a2.create()

        a1.fomtest = a2

        self.assertEqual(a1.fomtest.uid, a2.uid)

    def testMissingValue(self):
        a1 = self.A()
        a1.create()
        try:
            a1.fomtest2
        except Fluid404Error:
            pass
        else:
            self.fail('Failed to raise Fluid404Error')

    def testValue(self):
        a1 = self.A()
        a1.create()
        a1.fomtest2 = 'hello'
        self.assertEquals(a1.fomtest2, 'hello')


class ManagerTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

        n = Namespace(u'test')
        try:
            self.ns = n.create_namespace(u'fomtest', u'namespace for tag')
        except Fluid412Error:
            self.ns = n.namespace(u'fomtest')
        for name in (u'fomtest', u'fomtest2', u'fomtestrev'):
            try:
                n.create_tag(name, u'%s description' % name, False)
            except Fluid412Error:
                pass

        class A(Object):
            fomtest = tag_collection(u'test/fomtest')

        class B(Object):
            fomtestrev = tag_collection(u'test/fomtestrev', map_type=A,
                                     foreign_tagpath=u'test/fomtest')

        self.A = A
        self.B = B

    def test_add(self):
        a1 = self.A()
        a1.create()
        a2 = self.A()
        a2.create()
        a1.fomtest.add(a2)
        assert a2 in a1.fomtest

    def test_del(self):
        a1 = self.A()
        a1.create()
        a2 = self.A()
        a2.create()
        a1.fomtest.add(a2)
        assert a2 in a1.fomtest
        a1.fomtest.remove(a2)
        assert not a2 in a1.fomtest

    def test_foreign(self):
        a = self.A()
        a.create()
        b = self.B()
        b.create()
        b.fomtestrev.add(a)
        assert a in b.fomtestrev
        assert b in a.fomtest

    def test_foreign_delete(self):
        a = self.A()
        a.create()
        b = self.B()
        b.create()
        b.fomtestrev.add(a)
        assert a in b.fomtestrev
        assert b in a.fomtest
        b.fomtestrev.remove(a)
        assert a not in b.fomtestrev
        assert b not in a.fomtest


class TagRelationsTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()
        n = Namespace(u'test')
        try:
            self.ns = n.create_namespace(u'fomtest', u'namespace for tag')
        except Fluid412Error:
            self.ns = n.namespace(u'fomtest')
        for name in (u'fomtest', u'fomtest2', u'fomtestrev'):
            try:
                n.create_tag(name, u'%s description' % name, False)
            except Fluid412Error:
                pass

        class A(Object):
            fomtest2 = tag_value(u'test/fomtest2')

        class B(Object):
            fomtest = tag_relations(u'test/fomtest', A)

        self.A = A
        self.B = B

    def testSetRelations(self):
        a1 = self.A()
        a2 = self.A()
        a3 = self.A()
        a1.create()
        a2.create()
        a3.create()
        b = self.B()
        b.create()
        b.fomtest = [a1, a2, a3]
        self.assertEqual(b.fomtest, [a1, a2, a3])


if __name__ == '__main__':
    unittest.main()
