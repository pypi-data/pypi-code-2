#
# Skeleton ProtectedFileTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ProtectedFile.tests import ProtectedFileTestCase
from Products.ProtectedFile.utils import KeyManager
from DateTime import DateTime


class TestSetup(ProtectedFileTestCase.ProtectedFileTestCase):

    def testPortalSkins(self):
        self.failUnless('ProtectedFile' in self.portal.portal_skins.objectIds(),
                        'Skin was not installed')

    def testPortalTypes(self):
        self.failUnless('Protected File' in self.portal.portal_types.objectIds(),
                        'Portal type was not installed')


class TestProtectedFile(ProtectedFileTestCase.ProtectedFileTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Protected File', id='file')
        self.file = self.folder.file

    def testEmptyMapping(self):
        self.assertEqual(len(self.file.getKeys()), 0)

    def testAddToken(self):
        self.file.addToken('foo@bar.com')
        keys = self.file.getKeys()
        self.assertEqual(len(keys), 1)

    def testAddTokenSameEmail(self):
        self.file.addToken('foo@bar.com')
        self.file.addToken('foo@bar.com')
        keys = self.file.getKeys()
        self.assertEqual(len(keys), 2)

    def testConfimKey(self):
        key = self.file.addToken('foo@bar.com')
        self.failUnless(self.file.confirmKey(key))

    def testIsConfimedKey(self):
        key1 = self.file.addToken('foo@bar.com')
        key2 = self.file.addToken('baz@bar.com')
        self.file.confirmKey(key1)
        self.failUnless(self.file.isConfirmedKey(key1))
        self.failIf(self.file.isConfirmedKey(key2))

    def testConfimKeyIncreaseDownload(self):
        key = self.file.addToken('foo@bar.com')
        self.file.confirmKey(key)
        token = self.file.getKey(key)
        self.assertEqual(token.get('downloads'), 1)

    def testConfimKeyRejectsInvalidKey(self):
        key = self.file.addToken('foo@bar.com')
        bad_key = '12345'
        self.failIf(self.file.confirmKey(bad_key))
        bad_key = KeyManager().generate()
        self.failIf(self.file.confirmKey(bad_key))

    def testConfimKeyMultiple(self):
        key = self.file.addToken('foo@bar.com')
        token = self.file.getKey(key)
        self.file.confirmKey(key)
        self.file.confirmKey(key)
        self.assertEqual(token.get('downloads'), 2)


class TestDataAccess(ProtectedFileTestCase.ProtectedFileTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Protected File', id='file')
        self.file = self.folder.file
        self.file.edit(file='foo')
        self.key = self.file.addToken('foo@bar.com')
        self.file.confirmKey(self.key)

    def testGetDataMethodWithoutKeywordOrREQUESTAnonymous(self):
        self.logout()
        self.assertEqual(self.file.get_data(), None)

    def testGetDataMethodWithoutKeywordOrREQUESTAuthenticated(self):
        self.assertEqual(self.file.get_data(), 'foo')

    def testGetDataMethodWithKeywordAnonymous(self):
        self.logout()
        self.assertEqual(self.file.get_data(self.key), 'foo')

    def testGetDataMethodWithKeywordAuthenticated(self):
        self.assertEqual(self.file.get_data(self.key), 'foo')

    def testGetDataMethodWithREQUESTAnonymous(self):
        self.app.REQUEST.set('key', self.key)
        self.logout()
        self.assertEqual(self.file.get_data(), 'foo')

    def testGetDataMethodWithREQUESTAuthenticated(self):
        self.app.REQUEST.set('key', self.key)
        self.assertEqual(self.file.get_data(), 'foo')

    def testDataAttributeAnonymous(self):
        self.logout()
        self.assertEqual(self.file.data, None)

    def testDataAttributeAuthenticated(self):
        self.assertEqual(self.file.data, 'foo')


class TestListsAndCleanUp(ProtectedFileTestCase.ProtectedFileTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Protected File', id='file')
        self.file = self.folder.file
        self.key1 = self.file.addToken('key1@bar.com')
        self.key2 = self.file.addToken('same@bar.com')
        self.key3 = self.file.addToken('same@bar.com')
        self.key4 = self.file.addToken('key4@bar.com')
        self.key5 = self.file.addToken('key5@bar.com')
        twoWeeksAgo = DateTime() - 14
        token1 = self.file.getKey(self.key1)
        token1.update({'timestamp' : twoWeeksAgo})
        token2 = self.file.getKey(self.key2)
        token2.update({'timestamp' : twoWeeksAgo})
        self.file.confirmKey(self.key2)
        self.file.confirmKey(self.key3)
        self.file.confirmKey(self.key4)

    def testRemoveOldPengingItems(self):
        self.assertEqual(len(self.file.getKeys()), 4)
        self.failIf(self.key1 in self.file.getKeys().keys())

    def testKeepOldDownloadedItems(self):
        self.failUnless(self.key2 in self.file.getKeys().keys())

    def testKeepRecentPendingItems(self):
        self.failUnless(self.key4 in self.file.getKeys().keys())

    def testListTokensLength(self):
        self.assertEqual(len(self.file.listTokens()), 3)

    def testListTokensContainKeys(self):
        tokens = self.file.listTokens()
        token2 = self.file.getKey(self.key2)
        token3 = self.file.getKey(self.key3)
        token4 = self.file.getKey(self.key4)
        keys = [t.get('key') for t in tokens]
        self.failUnless(self.key2 in keys)
        self.failUnless(self.key3 in keys)
        self.failUnless(self.key4 in keys)

    def testListEmails(self):
        returned = self.file.listEmails()
        expected = ['same@bar.com', 'key4@bar.com']
        returned.sort()
        expected.sort()
        self.assertEqual(returned, expected)

    def testCountEmails(self):
        self.assertEqual(self.file.countEmails(), 2)


class TestToken(ProtectedFileTestCase.ProtectedFileTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Protected File', id='file')
        self.file = self.folder.file
        self.key = self.file.addToken('foo@bar.com')
        self.keys = self.file.getKeys()
        self.token = self.file.getKey(self.key)

    def testKeyExists(self):
        self.failUnless(self.keys.has_key(self.key))

    def testKeyIsValid(self):
        self.failUnless(KeyManager().verify(self.key))

    def testTokenStructure(self):
        self.failUnless(self.token.has_key('email'))
        self.failUnless(self.token.has_key('timestamp'))
        self.failUnless(self.token.has_key('downloads'))

    def testTokenEmail(self):
        self.assertEqual(self.token.get('email'), 'foo@bar.com')

    def testTokenTimestamp(self):
        self.failUnless(isinstance(self.token.get('timestamp'), DateTime))

    def testTokenDownloads(self):
        self.assertEqual(self.token.get('downloads'), 0)


class TestFunctionalProtectedFile(ZopeTestCase.Functional, ProtectedFileTestCase.ProtectedFileTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Protected File', id='file')
        self.file = self.folder.file
        self.file.edit(file='foo')
        self.file_path = '/'+self.file.absolute_url(1)
        self.basic_auth = '%s:secret' % ZopeTestCase.user_name
        self.pattern = 'Download Form'

    def testAbsoluteUrl(self):
        response = self.publish(self.file_path+'/absolute_url', self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().endswith('plone/Members/test_user_1_/file'))

    def testIndexWithoutKeyAnonymous(self):
        response = self.publish(self.file_path)
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) != -1)

    def testIndexWithoutKeyAuthenticated(self):
        response = self.publish(self.file_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) == -1)

    def testIndexWithAnyKeyAnonymous(self):
        response = self.publish(self.file_path+'?key=ABCDEF')
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) != -1)

    def testIndexWithAnyKeyAutheticated(self):
        response = self.publish(self.file_path+'?key=ABCDEF', self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) == -1)

    def testIndexWithValidKeyAnonymous(self):
        key = self.file.addToken('foo@bar.com')
        self.file.confirmKey(key)
        response = self.publish(self.file_path+'?key='+key)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), 'foo')

    def testIndexWithValidKeyAuthenticated(self):
        key = self.file.addToken('foo@bar.com')
        response = self.publish(self.file_path+'?key='+key, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), 'foo')

    def testDownloadWithoutKeyAnonymous(self):
        response = self.publish(self.file_path+'/download')
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) != -1)

    def testDownloadWithoutKeyAutheticated(self):
        response = self.publish(self.file_path+'/download', self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) == -1)

    def testDownloadWithAnyKeyAnonymous(self):
        response = self.publish(self.file_path+'/download?key=ABCDEF')
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) != -1)

    def testDownloadWithAnyKeyAuthenticated(self):
        response = self.publish(self.file_path+'/download?key=ABCDEF', self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.failUnless(response.getBody().find(self.pattern) == -1)

    def testDownloadWithValidKeyAnonymous(self):
        key = self.file.addToken('foo@bar.com')
        response = self.publish(self.file_path+'/download?key='+key)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), 'foo')

    def testDownloadWithValidKeyAuthenticated(self):
        key = self.file.addToken('foo@bar.com')
        response = self.publish(self.file_path+'/download?key='+key, self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), 'foo')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    suite.addTest(makeSuite(TestProtectedFile))
    suite.addTest(makeSuite(TestDataAccess))
    suite.addTest(makeSuite(TestListsAndCleanUp))
    suite.addTest(makeSuite(TestToken))
    suite.addTest(makeSuite(TestFunctionalProtectedFile))
    return suite

if __name__ == '__main__':
    framework()
