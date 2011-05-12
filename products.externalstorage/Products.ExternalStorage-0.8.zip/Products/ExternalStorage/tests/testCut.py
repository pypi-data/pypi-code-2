#
# Cut Tests
#

from Testing import ZopeTestCase

import os
from Products.ExternalStorage.tests import ESTestCase


class TestCutFile(ESTestCase.ESTestCase):

    # Tests the moving of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)
        self.folder.invokeFactory('Folder', id='new_folder')
        self.new_folder = getattr(self.folder, 'new_folder', None)
        cb = self.folder.manage_cutObjects([ESTestCase.FILENAME_DOC])
        res = self.new_folder.manage_pasteObjects(cb)

    def testOldRemovedFromZODB(self):
        self.failIf(ESTestCase.FILENAME_DOC in self.folder.objectIds())

    def testOldRemovedFromFileSystem(self):
        self.failIf(ESTestCase.FILENAME_DOC in os.listdir(ESTestCase.BASE_PATH))

    def testNewPresentOnZODB(self):
        self.failUnless(ESTestCase.FILENAME_DOC in self.new_folder.objectIds())

    def testNewPresentOnFileSystem(self):
        new_folder_path = os.path.join(ESTestCase.BASE_PATH, 'new_folder')
        self.failUnless(ESTestCase.FILENAME_DOC in os.listdir(new_folder_path))

    def testPathChangedOnStorage(self):
        path = os.path.join(ESTestCase.BASE_PATH, 'new_folder',
                            ESTestCase.FILENAME_DOC)
        art = getattr(self.new_folder, ESTestCase.FILENAME_DOC)
        field = art.getField('file')
        self.assertEqual(path, field.storage.getFilepath(art, 'file'))

    def testSameContentOnZODB(self):
        art = getattr(self.new_folder, ESTestCase.FILENAME_DOC)
        file_obj = art.getFile()
        self.assertEqual(ESTestCase.CONTENT_DOC, file_obj.data)

    def testSameContentOnFileSystem(self):
        path = os.path.join(ESTestCase.BASE_PATH, 'new_folder',
                            ESTestCase.FILENAME_DOC)
        self.assertEqual(ESTestCase.CONTENT_DOC, open(path, 'r').read())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCutFile))
    return suite
