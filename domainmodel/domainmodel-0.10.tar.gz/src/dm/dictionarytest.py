import dm.dictionary
from dm.dictionarywords import *
import unittest
import os
import mx.DateTime

def suite():
    suites = [
        unittest.makeSuite(TestSystemDictionary),
    ]
    return unittest.TestSuite(suites)


class TestSystemDictionary(unittest.TestCase):

    def setUp(self):
        self.dictionary = dm.dictionary.SystemDictionary()

    def test_systemName(self):
        self.failUnlessEqual(self.dictionary[SYSTEM_NAME], 'domainmodel')
        if self.dictionary[IMAGES_DIR_PATH]:
            imagesPath = self.dictionary[IMAGES_DIR_PATH]
            self.failUnless(os.path.exists(imagesPath), imagesPath)

    def test_systemUpSince(self):
        upSince = self.dictionary[SYSTEM_UP_SINCE]
        self.failUnless(upSince)
        self.failUnless(upSince < mx.DateTime.now())

