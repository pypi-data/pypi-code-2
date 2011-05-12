#
# ContentType Tests
#

from Testing import ZopeTestCase

from Products.ExternalStorage.tests import ESTestCase


class TestContentType(ESTestCase.ESTestCase):

    # Tests the content type updating of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)

    def testPrimaryFieldGetContentType(self):
        self.assertEqual('application/msword', self.art.getContentType())

    def testGetContentType(self):
        self.assertEqual('application/msword', self.art.getContentType('file'))

    def testUpdatePrimaryFieldContentType(self):
        self._updateContent(self.art, 'file', ESTestCase.DATAPATH_ZIP)
        self.assertEqual('application/zip', self.art.getContentType())

    def testUpdateContentType(self):
        self._updateContent(self.art, 'file', ESTestCase.DATAPATH_ZIP)
        self.assertEqual('application/zip', self.art.getContentType('file'))

    def testPrimaryFieldSetContentType(self):
        mimetype = 'image/jpeg'
        self.art.setContentType(mimetype)
        self.assertEqual(mimetype, self.art.getContentType())
        self.assertEqual(mimetype, self.art.getContentType('file'))

    def testSetContentType(self):
        mimetype = 'image/jpeg'
        self.art.setContentType(mimetype, 'file')
        self.assertEqual(mimetype, self.art.getContentType())
        self.assertEqual(mimetype, self.art.getContentType('file'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentType))
    return suite
