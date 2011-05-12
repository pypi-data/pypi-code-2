#
# Copy Tests
#

from Testing import ZopeTestCase

import os
from Products.ExternalStorage.tests import ESTestCase


class TestCopyFile(ESTestCase.ESTestCase):

    # Tests the copying of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)
        self.path = os.path.join(ESTestCase.BASE_PATH, ESTestCase.FILENAME_DOC)
        cb = self.folder.manage_copyObjects([ESTestCase.FILENAME_DOC])
        res = self.folder.manage_pasteObjects(cb)
        self.id_new = res[0]['new_id']
        self.path_new = os.path.join(ESTestCase.BASE_PATH, self.id_new)
        self.art_new = getattr(self.folder, self.id_new, None)

    def testIdHasChanged(self):
        self.assertNotEqual(ESTestCase.FILENAME_DOC, self.id_new)

    def testOldRemainsOnZODB(self):
        self.failUnless(ESTestCase.FILENAME_DOC in self.folder.objectIds())

    def testOldRemainsOnFileSystem(self):
        self.failUnless(ESTestCase.FILENAME_DOC in
                        os.listdir(ESTestCase.BASE_PATH))

    def testNewPresentOnZODB(self):
        self.failUnless(self.id_new in self.folder.objectIds())

    def testNewPresentOnFileSystem(self):
        self.failUnless(self.id_new in os.listdir(ESTestCase.BASE_PATH))

    def testPathChangedOnStorage(self):
        field = self.art.getField('file')
        field_new = self.art_new.getField('file')
        self.assertNotEqual(field.storage.getFilepath(self.art, 'file'),
                            field_new.storage.getFilepath(self.art_new, 'file'))

    def testSameContentOnZODB(self):
        file_obj1 = self.art.getFile()
        file_obj2 = self.art_new.getFile()
        self.assertEqual(file_obj1.data, file_obj2.data)
        self.assertNotEqual(file_obj1.filename, file_obj2.filename)

    def testSameContentOnFileSystem(self):
        self.assertEqual(open(self.path, 'r').read(),
                         open(self.path_new, 'r').read())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCopyFile))
    return suite
