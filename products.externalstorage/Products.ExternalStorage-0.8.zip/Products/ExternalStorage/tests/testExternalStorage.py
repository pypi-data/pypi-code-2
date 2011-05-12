#
# Tests the ExternalStorage
#

from Testing import ZopeTestCase

from Products.ExternalStorage.tests import ESTestCase


class TestExternalStorage(ESTestCase.ESTestCase):

    def testExternalExampleInstalable(self):
        qi_tool = self.portal.portal_quickinstaller
        self.failUnless(qi_tool.isProductInstallable('ExternalExample'))

    def testExternalArticleInstalled(self):
        types_tool = self.portal.portal_types
        self.failUnless('ExternalArticle' in types_tool.objectIds())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExternalStorage))
    return suite
