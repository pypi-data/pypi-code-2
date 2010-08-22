import uuid

import unittest

from fom.dev import sandbox_fluid
from fom.db import FluidDB
from fom.errors import Fluid404Error
from fom.api import (UserApi, UsersApi, NamespaceApi, NamespacesApi,
    TagApi, TagsApi, ObjectsApi, PermissionsApi)


class TestUsersApi(unittest.TestCase):

    def setUp(self):
        self.db = FluidDB('http://sandbox.fluidinfo.com')
        self.users = UsersApi(self.db)

    def testUserApi(self):
        user_api = self.users['aliafshar']
        self.assertTrue(isinstance(user_api, UserApi))
        self.assertEquals(user_api.username, 'aliafshar')

    def testUserGet(self):
        r = self.users[u'aliafshar'].get()
        self.assertEquals(r.status, 200)
        self.assertEquals(r.value[u'name'], u'aliafshar')


class TestNamespaceApi(unittest.TestCase):

    def setUp(self):
        self.uid = str(uuid.uuid4())
        self.path = 'test/%s' % self.uid
        self.db = FluidDB('http://sandbox.fluidinfo.com')
        self.namespaces = NamespacesApi(self.db)

    def testNamespaceApi(self):
        ns_api = self.namespaces['test']
        self.assertEquals(ns_api.path, 'test')

    def testNamespaceGet(self):
        ns_api = self.namespaces['test']
        r = ns_api.get()
        self.assertEquals(r.status,  200)
        self.assertTrue(u'description' not in r.value)
        self.assertTrue(u'tagNames' not in r.value)
        self.assertTrue(u'namespaceNames' not in r.value)

    def testNamespaceGetDescription(self):
        ns_api = self.namespaces['test']
        r = ns_api.get(returnDescription=True)
        self.assertTrue(r.value[u'description'].startswith(u'FluidDB user'))

    def testNamespaceGetTags(self):
        ns_api = self.namespaces['test']
        r = ns_api.get(returnTags=True)
        self.assertTrue(u'tagNames' in r.value)

    def testNamespaceGetNamespaces(self):
        ns_api = self.namespaces['test']
        r = ns_api.get(returnNamespaces=True)
        self.assertTrue(u'namespaceNames' in r.value)

    def testNamespacePost(self):
        self.db.login('test', 'test')
        ns_api = self.namespaces['test']
        r = ns_api.post(name=self.uid, description=u'test desc')
        self.assertEquals(r.status, 201)
        r = self.namespaces[self.path].get()
        self.assertEquals(r.status, 200)
        r = self.namespaces[self.path].delete()
        self.assertEquals(r.status, 204)

    def testNamespaceDelete(self):
        self.db.login('test', 'test')
        ns_api = self.namespaces['test']
        r = ns_api.post(name=self.uid, description=u'test desc')
        self.assertEquals(r.status, 201)
        r = self.namespaces[self.path].get()
        self.assertEquals(r.status, 200)
        r = self.namespaces[self.path].delete()
        self.assertEquals(r.status, 204)
        self.assertRaises(Fluid404Error, self.namespaces[self.path].get)


class TestTagsApi(unittest.TestCase):

    def setUp(self):
        self.db = FluidDB('http://sandbox.fluidinfo.com')
        self.db.login('test', 'test')
        self.tags = TagsApi(self.db)
        self.uid = str(uuid.uuid4())
        self.path = 'test/%s' % self.uid

    def test_get(self):
        r = self.tags['fluiddb/about'].get(returnDescription=True)
        self.assertEquals(r.status, 200)
        self.assertTrue(r.value[u'description'].startswith(u'A description of'))

    def test_post(self):
        self.assertRaises(Fluid404Error, self.tags[self.path].get)
        r = self.tags['test'].post(self.uid, u'test', False)
        # print r
        self.assertEquals(r.status, 201)
        r = self.tags[self.path].get()
        self.assertEquals(r.status, 200)
        r = self.tags[self.path].delete()
        # print r

    def test_put(self):
        r = self.tags['test'].post(self.uid, u'test', False)
        self.assertEquals(r.status, 201)
        r = self.tags[self.path].get()
        self.assertEquals(r.status, 200)
        r = self.tags[self.path].put(u'new desc')
        self.assertEquals(r.status, 204)
        r = self.tags[self.path].get(returnDescription=True)
        self.assertEquals(r.status, 200)
        self.assertEquals(r.value[u'description'], u'new desc')
        r = self.tags[self.path].delete()

    def test_delete(self):
        self.assertRaises(Fluid404Error, self.tags[self.path].get)
        r = self.tags['test'].post(self.uid, u'test', False)
        self.assertEquals(r.status, 201)
        r = self.tags[self.path].get()
        self.assertEquals(r.status, 200)
        r = self.tags[self.path].delete()
        self.assertRaises(Fluid404Error, self.tags[self.path].get)


class TestObjectsApi(unittest.TestCase):

    def setUp(self):
        self.db = FluidDB('http://sandbox.fluidinfo.com')
        self.objects = ObjectsApi(self.db)

    def testGetQuery(self):
        r = self.objects.get('fluiddb/about = 1')
        self.assertTrue('ids' in r.value)

    def testPostObjects(self):
        r = self.objects.post()
        self.assertEquals(r.status, 201)
        r = self.objects[r.value[u'id']].get(showAbout=True)
        self.assertEquals(r.status, 200)
        self.assertTrue(r.value[u'about'] is None)

    def testPostObjectsAbout(self):
        r = self.objects.post(about=u'Something About')
        self.assertEquals(r.status, 201)
        r = self.objects[r.value[u'id']].get(showAbout=True)
        self.assertEquals(r.status, 200)
        self.assertEquals(r.value[u'about'], u'Something About')


class TestPermissionApi(unittest.TestCase):

    def setUp(self):
        self.db = FluidDB('http://sandbox.fluidinfo.com')
        self.db.login('test', 'test')
        self.permissions = PermissionsApi(self.db)

    def testGetNamespacePerm(self):
        api = self.permissions.namespaces
        r = api[u'test'].get(u'list')
        self.assertEquals(r.status, 200)

    def testPutNamespacePerm(self):
        # create a new namespace
        uid = str(uuid.uuid4())
        tl_api = NamespaceApi(u'test', self.db)
        tl_api.post(uid, u'test')
        ns_api = NamespaceApi(u'test/%s' % uid, self.db)
        r = self.permissions.namespaces[ns_api.path].put(u'list', u'open', [])
        self.assertEquals(r.status, 204)
        r = self.permissions.namespaces[ns_api.path].get(u'list')
        self.assertEquals(r.status, 200)
        self.assertEquals(r.value[u'policy'], u'open')
        self.assertEquals(r.value[u'exceptions'], [])
        # clean up
        ns_api.delete()

    def testGetTagsPerm(self):
        uid = str(uuid.uuid4())
        tagpath = u'test/%s' % uid
        # now a new tag
        tag_api = TagApi(u'test', self.db)
        r = tag_api.post(uid, u'test', False)
        self.assertEquals(r.status, 201)
        api = self.permissions.tags[tagpath]
        r = api.get('update')
        self.assertEquals(r.status, 200)

    def testPutTagsPerm(self):
        uid = str(uuid.uuid4())
        tagpath = u'test/%s' % uid
        # now a new tag
        tag_api = TagApi(u'test', self.db)
        r = tag_api.post(uid, u'test', False)
        self.assertEquals(r.status, 201)
        r = self.permissions.tags[tagpath].put(u'update', u'open', [])
        self.assertEquals(r.status, 204)
        r = self.permissions.tags[tagpath].get(u'update')
        self.assertEquals(r.status, 200)
        self.assertEquals(r.value[u'policy'], u'open')
        self.assertEquals(r.value[u'exceptions'], [])
        # clean up
        TagApi(tagpath, self.db).delete()

    def testGetTagValuesPerm(self):
        uid = str(uuid.uuid4())
        tagpath = u'test/%s' % uid
        # now a new tag
        tag_api = TagApi(u'test', self.db)
        r = tag_api.post(uid, u'test', False)
        self.assertEquals(r.status, 201)
        api = self.permissions.tag_values[tagpath]
        r = api.get('see')
        self.assertEquals(r.status, 200)


    def testPutTagValuesPerm(self):
        uid = str(uuid.uuid4())
        tagpath = u'test/%s' % uid
        # now a new tag
        tag_api = TagApi(u'test', self.db)
        r = tag_api.post(uid, u'test', False)
        self.assertEquals(r.status, 201)
        r = self.permissions.tag_values[tagpath].put(u'see', u'open', [])
        self.assertEquals(r.status, 204)
        r = self.permissions.tag_values[tagpath].get(u'see')
        self.assertEquals(r.status, 200)
        self.assertEquals(r.value[u'policy'], u'open')
        self.assertEquals(r.value[u'exceptions'], [])
        # clean up
        TagApi(tagpath, self.db).delete()


class PoliciesTest(unittest.TestCase):

    def setUp(self):
        self.fluid = sandbox_fluid()

    def test_get(self):
        r = self.fluid.policies[
            'test', 'namespaces', 'list'].get()
        self.assertEquals(r.value[u'policy'], u'open')

    def test_put(self):
        r = self.fluid.policies[
            'test', 'namespaces', 'list'].put(u'open', [])
        self.assertEquals(r.status, 204)


if __name__ == '__main__':
    unittest.main()
