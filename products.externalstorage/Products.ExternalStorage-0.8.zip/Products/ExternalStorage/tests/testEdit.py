#
# Edit Tests
#

from Testing import ZopeTestCase

import os
from OFS.Image import File
from Products.ExternalStorage.tests import ESTestCase
from Products.ATContentTypes.content.base import cleanupFilename


class TestEditFile(ESTestCase.ESTestCase):

    # Tests the editing of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)
        self.path = os.path.join(ESTestCase.BASE_PATH,
                                 ESTestCase.FILENAME_ZIP)
        self._updateContent(self.art, 'file', ESTestCase.DATAPATH_ZIP)

    def testEditedObjectChangedId(self):
        self.assertEqual(ESTestCase.FILENAME_ZIP, self.art.getId())

    def testOldRemovedFromZODB(self):
        self.failIf(ESTestCase.FILENAME_DOC in self.folder.objectIds())

    def testOldRemovedFromFileSystem(self):
        self.failIf(ESTestCase.FILENAME_DOC in os.listdir(ESTestCase.BASE_PATH))

    def testEditedPresentOnZODB(self):
        self.failUnless(ESTestCase.FILENAME_ZIP in self.folder.objectIds())

    def testEditedPresentOnFileSystem(self):
        self.failUnless(ESTestCase.FILENAME_ZIP in
                        os.listdir(ESTestCase.BASE_PATH))

    def testPathChangedOnStorage(self):
        field = self.art.getField('file')
        self.assertEqual(self.path, field.storage.getFilepath(self.art, 'file'))

    def testSameContentOnZODB(self):
        file_obj = self.art.getFile()
        self.assertEqual(ESTestCase.CONTENT_ZIP, str(file_obj.data))

    def testTypeContentOnZODB(self):
        file_obj = self.art.getFile()
        self.failUnless(isinstance(file_obj, File))

    def testSameContentOnFileSystem(self):
        self.assertEqual(ESTestCase.CONTENT_ZIP, open(self.path, 'r').read())


class TestIllegalFilename(ESTestCase.ESTestCase):

    # Tests the editing of an external article containing illegal
    # chars on filename

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC_CHARS)
        self.path = os.path.join(ESTestCase.BASE_PATH,
                                 ESTestCase.FILENAME_ZIP_CHARS)
        self._updateContent(self.art, 'file', ESTestCase.DATAPATH_ZIP_CHARS)
        self.cleaned_id = cleanupFilename(ESTestCase.FILENAME_ZIP_CHARS)

    def testEditedObjectCleanedId(self):
        self.assertEqual(self.cleaned_id, self.art.getId())

    def testEditedObjectPath(self):
        cleaned_path = os.path.join(ESTestCase.BASE_PATH, self.cleaned_id)
        field = self.art.getField('file')
        self.assertEqual(cleaned_path,
                         field.storage.getFilepath(self.art, 'file'))

    def testEditedPresentOnZODB(self):
        self.failUnless(self.cleaned_id in self.folder.objectIds())

    def testEditedPresentOnFileSystem(self):
        self.failUnless(self.cleaned_id in os.listdir(ESTestCase.BASE_PATH))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEditFile))
    return suite
