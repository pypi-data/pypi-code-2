#
# Filename Tests
#

from Testing import ZopeTestCase

from Products.ExternalStorage.tests import ESTestCase


class TestFilename(ESTestCase.ESTestCase):

    # Tests the filename updating of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)

    def testPrimaryFieldGetFilename(self):
        self.assertEqual(ESTestCase.FILENAME_DOC, self.art.getFilename())

    def testFieldGetFilename(self):
        self.assertEqual(ESTestCase.FILENAME_DOC, self.art.getFilename('file'))

    def testUpdatePrimaryFieldFilename(self):
        self._updateContent(self.art, 'file', ESTestCase.DATAPATH_ZIP)
        self.assertEqual(ESTestCase.FILENAME_ZIP, self.art.getFilename())

    def testUpdateFilename(self):
        self._updateContent(self.art, 'file', ESTestCase.DATAPATH_ZIP)
        self.assertEqual(ESTestCase.FILENAME_ZIP, self.art.getFilename('file'))

    def testPrimaryFieldSetFilename(self):
        filename = 'photo.jpg'
        self.art.setFilename(filename)
        self.assertEqual(filename, self.art.getFilename())
        self.assertEqual(filename, self.art.getFilename('file'))

    def testSetFilename(self):
        filename = 'photo.jpg'
        self.art.setFilename(filename, 'file')
        self.assertEqual(filename, self.art.getFilename())
        self.assertEqual(filename, self.art.getFilename('file'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFilename))
    return suite
