#
# Add Tests
#

from Testing import ZopeTestCase

import os
from OFS.Image import File
from Products.ExternalStorage.tests import ESTestCase
from Products.ATContentTypes.content.base import cleanupFilename


class TestAddFileViaString(ESTestCase.ESTestCase):

    # Tests the adding of an external article with a string value.

    def afterSetUp(self):
        self.art = self._addFileByString(self.folder, 'file',
                                         ESTestCase.FILENAME_DOC)
        self.path = os.path.join(ESTestCase.BASE_PATH,
                                 ESTestCase.FILENAME_DOC)

    def testAddedObjectId(self):
        self.assertEqual(ESTestCase.FILENAME_DOC, self.art.getId())

    def testAddedObjectContent(self):
        file_obj = self.art.getFile()
        self.assertEqual(ESTestCase.CONTENT_TXT, file_obj.data)

    def testAddedTypeContentOnZODB(self):
        data = self.art.getFile()
        self.failUnless(isinstance(data, File))

    def testAddedFileContent(self):
        self.assertEqual(ESTestCase.CONTENT_TXT, open(self.path, 'r').read())

    def testAddedObjectPath(self):
        field = self.art.getField('file')
        self.assertEqual(self.path, field.storage.getFilepath(self.art, 'file'))

    def testAddedFileSystemPresence(self):
        self.failUnless(ESTestCase.FILENAME_DOC in
                        os.listdir(ESTestCase.BASE_PATH))


class TestAddFileViaUploadFile(ESTestCase.ESTestCase):

    # Tests the adding of an external article with a FileUpload object.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)
        self.path = os.path.join(ESTestCase.BASE_PATH,
                                 ESTestCase.FILENAME_DOC)

    def testAddedObjectId(self):
        self.assertEqual(ESTestCase.FILENAME_DOC, self.art.getId())

    def testAddedObjectContent(self):
        file_obj = self.art.getFile()
        self.assertEqual(ESTestCase.CONTENT_DOC, file_obj.data)

    def testAddedTypeContentOnZODB(self):
        file_obj = self.art.getFile()
        self.failUnless(isinstance(file_obj, File))

    def testAddedFileContent(self):
        self.assertEqual(ESTestCase.CONTENT_DOC, open(self.path, 'r').read())

    def testAddedObjectPath(self):
        field = self.art.getField('file')
        self.assertEqual(self.path, field.storage.getFilepath(self.art, 'file'))

    def testAddedFileSystemPresence(self):
        self.failUnless(ESTestCase.FILENAME_DOC in
                        os.listdir(ESTestCase.BASE_PATH))


class TestMultipleAddFile(ESTestCase.ESTestCase):

    # Tests the multiple adding of external articles.

    def afterSetUp(self):
        self.art1 = self._addFileByFileUpload(self.folder, 'file',
                                              ESTestCase.FILENAME_DOC)
        self.folder.invokeFactory('ExternalArticle', id='art2')
        self.art2 = self.folder.art2

    def testAddedObjectId(self):
        self.assertEqual(ESTestCase.FILENAME_DOC, self.art1.getId())
        self.assertEqual('art2', self.art2.getId())

    def testAddedObjectContent(self):
        file1_obj = self.art1.getFile()
        file2_obj = self.art2.getFile()
        self.assertEqual(ESTestCase.CONTENT_DOC, str(file1_obj))
        self.assertEqual('', str(file2_obj))

    def testAddedTypeContentOnZODB(self):
        file1_obj = self.art1.getFile()
        file2_obj = self.art2.getFile()
        self.failUnless(isinstance(file1_obj, File))
        self.failUnless(isinstance(file2_obj, File))

    def testAddedObjectPath(self):
        field1 = self.art1.getField('file')
        field2 = self.art2.getField('file')
        path1 = os.path.join(ESTestCase.BASE_PATH, ESTestCase.FILENAME_DOC)
        path2 = os.path.join(ESTestCase.BASE_PATH, 'art2')
        self.assertEqual(path1, field1.storage.getFilepath(self.art1, 'file'))
        self.assertEqual(path2, field2.storage.getFilepath(self.art2, 'file'))

    def testAddedFileSystemPresence(self):
        self.failUnless(ESTestCase.FILENAME_DOC in
                        os.listdir(ESTestCase.BASE_PATH))
        self.failUnless('art2' in
                        os.listdir(ESTestCase.BASE_PATH))


class TestIllegalFilename(ESTestCase.ESTestCase):

    # Tests the adding of an external article with a FileUpload object
    # containing illegal chars on filename

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC_CHARS)
        self.cleaned_id = cleanupFilename(ESTestCase.FILENAME_DOC_CHARS)

    def testAddedObjectCleanedId(self):
        self.assertEqual(self.cleaned_id, self.art.getId())

    def testAddedObjectPath(self):
        cleaned_path = os.path.join(ESTestCase.BASE_PATH, self.cleaned_id)
        field = self.art.getField('file')
        self.assertEqual(cleaned_path,
                         field.storage.getFilepath(self.art, 'file'))

    def testAddedFileSystemPresence(self):
        self.failUnless(self.cleaned_id in os.listdir(ESTestCase.BASE_PATH))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAddFileViaString))
    suite.addTest(makeSuite(TestAddFileViaUploadFile))
    suite.addTest(makeSuite(TestMultipleAddFile))
    suite.addTest(makeSuite(TestIllegalFilename))
    return suite
