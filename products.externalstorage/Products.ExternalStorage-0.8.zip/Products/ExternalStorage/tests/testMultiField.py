#
# Multi Field Tests
#

from Testing import ZopeTestCase

import os
from Products.ExternalStorage.tests import ESTestCase
from Products.ATContentTypes.content.base import cleanupFilename


class TestMultiField(ESTestCase.ESTestCase):
    """Tests the multi-field support.
    """

    def afterSetUp(self):
        self.complex = self._addFileByFileUpload(self.folder, 'file_external1',
                                                 ESTestCase.FILENAME_DOC,
                                                 'ComplexSample')
        self._updateContent(self.complex, 'file_external2',
                            ESTestCase.DATAPATH_ZIP)
        self._updateContent(self.complex, 'file_external3',
                            ESTestCase.DATAPATH_ZIP_CHARS)
        self.path = os.path.join(ESTestCase.BASE_PATH, ESTestCase.FILENAME_DOC)

    def testAddedObjectId(self):
        self.assertEqual(ESTestCase.FILENAME_DOC, self.complex.getId())

    def testAddedObjectContent(self):
        self.assertEqual(ESTestCase.CONTENT_DOC,
                         self.complex.getFileExternal1().data)
        self.assertEqual(ESTestCase.CONTENT_ZIP,
                         self.complex.getFileExternal2().data)
        self.assertEqual(ESTestCase.CONTENT_ZIP_CHARS,
                         self.complex.getFile_external3().data)

    def testAddedFileContent(self):
        self.assertEqual(ESTestCase.CONTENT_DOC,
                         open(self.path + '/file_external1', 'r').read())
        self.assertEqual(ESTestCase.CONTENT_ZIP,
                         open(self.path + '/file_external2', 'r').read())
        path = ESTestCase.BASE_PATH_MISC + '/' + ESTestCase.FILENAME_DOC
        self.assertEqual(ESTestCase.CONTENT_ZIP_CHARS,
                         open(path, 'r').read())

    def testAddedObjectPath(self):
        storage1 = self.complex.getField('file_external1').storage
        storage2 = self.complex.getField('file_external2').storage
        storage3 = self.complex.getField('file_external3').storage
        self.assertEqual(self.path + '/file_external1',
                         storage1.getFilepath(self.complex, 'file_external1'))
        self.assertEqual(self.path + '/file_external2',
                         storage2.getFilepath(self.complex, 'file_external2'))
        self.assertEqual(ESTestCase.BASE_PATH_MISC + ESTestCase.FILENAME_DOC,
                         storage3.getFilepath(self.complex, 'file_external3'))

    def testFileSystemPresence(self):
        instance_path = ESTestCase.BASE_PATH + '/' + ESTestCase.FILENAME_DOC
        self.failUnless('file_external1' in os.listdir(instance_path))
        self.failUnless('file_external2' in os.listdir(instance_path))
        self.failUnless(ESTestCase.FILENAME_DOC in
                        os.listdir(ESTestCase.BASE_PATH_MISC))

    def testSetContentType(self):
        self.assertEqual('application/msword',
                         self.complex.getContentType('file_external1'))
        self.assertEqual('application/zip',
                         self.complex.getContentType('file_external2'))
        self.assertEqual('application/zip',
                         self.complex.getContentType('file_external3'))

    def testFieldGetFilename(self):
        cleaned_id = cleanupFilename(ESTestCase.FILENAME_ZIP_CHARS)
        self.assertEqual(ESTestCase.FILENAME_DOC,
                         self.complex.getFilename('file_external1'))
        self.assertEqual(ESTestCase.FILENAME_ZIP,
                         self.complex.getFilename('file_external2'))
        self.assertEqual(cleaned_id,
                         self.complex.getFilename('file_external3'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMultiField))
    return suite
