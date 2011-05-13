#
# Delete Tests
#

from Testing import ZopeTestCase

import os
from Products.ExternalStorage.tests import ESTestCase


class TestDeleteFile(ESTestCase.ESTestCase):

    # Tests the deleting of an external article.

    def afterSetUp(self):
        self.art = self._addFileByFileUpload(self.folder, 'file',
                                             ESTestCase.FILENAME_DOC)
        self.folder.manage_delObjects([ESTestCase.FILENAME_DOC])

    def testRemovedFromZODB(self):
        self.failIf(ESTestCase.FILENAME_DOC in self.folder.objectIds())

    def testRemovedFromFileSystem(self):
        self.failIf(ESTestCase.FILENAME_DOC in os.listdir(ESTestCase.BASE_PATH))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeleteFile))
    return suite
