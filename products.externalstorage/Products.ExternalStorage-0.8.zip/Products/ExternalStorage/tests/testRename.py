#
# Rename Tests
#

from Testing import ZopeTestCase

import os
from OFS.Image import File
from Products.ExternalStorage.tests import ESTestCase


class TestRenameFile(ESTestCase.ESTestCase):

    # Tests the renaming of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)
        self.folder.manage_renameObject(self.art.getId(), ESTestCase.FILENAME_DOC_NEW)
        self.path = os.path.join(ESTestCase.BASE_PATH, ESTestCase.FILENAME_DOC)
        self.path_new = os.path.join(ESTestCase.BASE_PATH, ESTestCase.FILENAME_DOC_NEW)

    def testOldRemovedFromZODB(self):
        self.failIf(ESTestCase.FILENAME_DOC in self.folder.objectIds())

    def testOldRemovedFromFileSystem(self):
        self.failIf(ESTestCase.FILENAME_DOC in os.listdir(ESTestCase.BASE_PATH))

    def testNewPresentOnZODB(self):
        self.failUnless(ESTestCase.FILENAME_DOC_NEW in self.folder.objectIds())

    def testNewPresentOnFileSystem(self):
        self.failUnless(ESTestCase.FILENAME_DOC_NEW in
                        os.listdir(ESTestCase.BASE_PATH))

    def testPathChangedOnStorage(self):
        art_new = getattr(self.folder, ESTestCase.FILENAME_DOC_NEW)
        field = art_new.getField('file')
        self.assertEqual(self.path_new,
                         field.storage.getFilepath(art_new, 'file'))

    def testSameContentOnZODB(self):
        art_new = getattr(self.folder, ESTestCase.FILENAME_DOC_NEW)
        file_obj = art_new.getFile()
        self.assertEqual(ESTestCase.CONTENT_DOC, str(file_obj.data))

    def testTypeContentOnZODB(self):
        art_new = getattr(self.folder, ESTestCase.FILENAME_DOC_NEW)
        file_obj = art_new.getFile()
        self.failUnless(isinstance(file_obj, File))

    def testSameContentOnFileSystem(self):
        self.assertEqual(ESTestCase.CONTENT_DOC, open(self.path_new, 'r').read())

    def testFilenameChanged(self):
        art_new = getattr(self.folder, ESTestCase.FILENAME_DOC_NEW)
        field = art_new.getField('file')
        self.assertEqual(ESTestCase.FILENAME_DOC_NEW,
                         field.storage.getFilename(art_new, 'file'))


class TestRenameParentFolder(ESTestCase.ESTestCase):

    # Tests the renaming of the parent folder from an external article.

    def afterSetUp(self):
        self.folder.invokeFactory('Folder', id='art_folder')
        self.art_folder = getattr(self.folder, 'art_folder', None)
        self.art1 = self._addFileByFileUpload(self.art_folder, 'file',
                                              ESTestCase.FILENAME_DOC)
        self.art2 = self._addFileByFileUpload(self.art_folder, 'file',
                                              ESTestCase.FILENAME_ZIP)
        self.path1 = os.path.join(ESTestCase.BASE_PATH, 'art_folder',
                                  ESTestCase.FILENAME_DOC)
        self.path2 = os.path.join(ESTestCase.BASE_PATH, 'art_folder',
                                  ESTestCase.FILENAME_ZIP)
        self.folder.manage_renameObject('art_folder', 'art_folder_new')
        self.art_folder_new = getattr(self.folder, 'art_folder_new')
        self.art1_new = getattr(self.art_folder_new, ESTestCase.FILENAME_DOC)
        self.art2_new = getattr(self.art_folder_new, ESTestCase.FILENAME_ZIP)

    def testOldFolderRemovedFromFileSystem(self):
        # This test currently fails
        self.failIf('art_folder' in os.listdir(ESTestCase.BASE_PATH))

    def testOldFilesRemovedFromFileSystem(self):
        self.failIf(ESTestCase.FILENAME_DOC in
                    os.listdir(ESTestCase.BASE_PATH + 'art_folder'))
        self.failIf(ESTestCase.FILENAME_ZIP in
                    os.listdir(ESTestCase.BASE_PATH + 'art_folder'))

    def testNewObjectsPresentOnZODB(self):
        self.failUnless(ESTestCase.FILENAME_DOC in self.art_folder_new.objectIds())
        self.failUnless(ESTestCase.FILENAME_ZIP in self.art_folder_new.objectIds())

    def testNewFilesPresentOnFileSystem(self):
        self.failUnless(ESTestCase.FILENAME_DOC in
                        os.listdir(ESTestCase.BASE_PATH + 'art_folder_new'))
        self.failUnless(ESTestCase.FILENAME_ZIP in
                        os.listdir(ESTestCase.BASE_PATH + 'art_folder_new'))

    def testPathChangedOnStorage(self):
        field1 = self.art1_new.getField('file')
        field2 = self.art2_new.getField('file')
        path1_new = os.path.join(ESTestCase.BASE_PATH, 'art_folder_new',
                                 ESTestCase.FILENAME_DOC)
        path2_new = os.path.join(ESTestCase.BASE_PATH, 'art_folder_new',
                                 ESTestCase.FILENAME_ZIP)
        self.assertEqual(path1_new,
                         field1.storage.getFilepath(self.art1_new, 'file'))
        self.assertEqual(path2_new,
                         field2.storage.getFilepath(self.art2_new, 'file'))

    def testSameContentOnZODB(self):
        file1_obj = self.art1_new.getFile()
        file2_obj = self.art2_new.getFile()
        self.assertEqual(ESTestCase.CONTENT_DOC, file1_obj.data)
        self.assertEqual(ESTestCase.CONTENT_ZIP, file2_obj.data)

    def testSameContentOnFileSystem(self):
        path1_new = os.path.join(ESTestCase.BASE_PATH, 'art_folder_new',
                                 ESTestCase.FILENAME_DOC)
        path2_new = os.path.join(ESTestCase.BASE_PATH, 'art_folder_new',
                                 ESTestCase.FILENAME_ZIP)
        self.assertEqual(ESTestCase.CONTENT_DOC, open(path1_new, 'r').read())
        self.assertEqual(ESTestCase.CONTENT_ZIP, open(path2_new, 'r').read())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRenameFile))
    suite.addTest(makeSuite(TestRenameParentFolder))
    return suite
