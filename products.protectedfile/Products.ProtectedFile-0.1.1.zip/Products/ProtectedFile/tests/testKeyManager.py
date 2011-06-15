#
# KeyManager tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ProtectedFile.tests import ProtectedFileTestCase
from Products.ProtectedFile.utils import KeyManager
from Products.ProtectedFile.utils import KEYLENGTH
from Products.ProtectedFile.utils import ALLOWED_CHARS


class TestKeyManager(ProtectedFileTestCase.ProtectedFileTestCase):

    def afterSetUp(self):
        self.km = KeyManager()
        self.key = self.km.generate()

    def testAllowedChars(self):
        self.assertEqual(len(ALLOWED_CHARS), 26)

    def testKeyLength(self):
        self.assertEqual(len(self.key), KEYLENGTH)

    def testKeyContents(self):
        for c in self.key:
            self.failUnless(c.isupper())

    def testKeyVariation(self):
        key2 = self.km.generate()
        self.failIfEqual(self.key, key2)

    def testKeyVerify(self):
        self.assertEqual(self.km.verify(self.key), True)
        self.assertEqual(self.km.verify('ABCD'), False)
        self.assertEqual(self.km.verify('abcdef'), False)

    def testKeyVerifyNone(self):
        self.assertEqual(self.km.verify(None), False)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestKeyManager))
    return suite

if __name__ == '__main__':
    framework()
