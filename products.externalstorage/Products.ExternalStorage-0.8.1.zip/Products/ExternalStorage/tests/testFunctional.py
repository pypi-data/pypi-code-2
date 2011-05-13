#
# Functional Tests
#

from Testing import ZopeTestCase

from Products.ExternalStorage.tests import ESTestCase


class TestDownload(ESTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.portal_path = '/' + self.portal.absolute_url(1)
        self.complex = self._addFileByFileUpload(self.folder, 'file_external1',
                                                 ESTestCase.FILENAME_DOC,
                                                 'ComplexSample')
        self._updateContent(self.complex, 'file_normal', ESTestCase.DATAPATH_ZIP)
        self.complex_url = '/' + self.complex.absolute_url(1)
        self.basic_auth = '%s:%s' % (ESTestCase.default_user,
                                     ESTestCase.default_password)

    def testArchetypesAnonymousAttributeStorageDownload(self):
        response = self.publish(self.complex_url+'/at_download/file_normal')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        content = str(self.complex.getFile_normal())
        self.failUnlessEqual(body, content)

    def testArchetypesAuthenticatedAttributeStorageDownload(self):
        response = self.publish(self.complex_url+'/at_download/file_normal',
                                self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        content = str(self.complex.getFile_normal())
        self.failUnlessEqual(body, content)

    def testArchetypesAnonymousExternalStorageDownload(self):
        response = self.publish(self.complex_url+'/at_download/file_external1')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        content = str(self.complex.getFileExternal1())
        self.failUnlessEqual(body, content)

    def testArchetypesAuthenticatedExternalStorageDownload(self):
        response = self.publish(self.complex_url+'/at_download/file_external1',
                                self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        content = str(self.complex.getFileExternal1())
        self.failUnlessEqual(body, content)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDownload))
    return suite

if __name__ == '__main__':
    framework()
