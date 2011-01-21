#
# Setup tests
#

from Products.UnicodeLexicon.tests import UnicodeLexiconTestCase
from Products.UnicodeLexicon.lexicon import UnicodeLexicon


class TestSetup(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def afterSetUp(self):
        self.setup = self.portal.portal_setup
        self.catalog = self.portal.portal_catalog
        # Delete existing logs to prevent race conditions
        self.setup.manage_delObjects(self.setup.objectIds())

    def testProfiles(self):
        ids = [x['id'] for x in self.setup.listProfileInfo()]
        self.failUnless('Products.UnicodeLexicon:default' in ids)

    def testCatalogLexicons(self):
        ids = self.catalog.objectIds()
        self.failUnless('unicode_plaintext_lexicon' in ids)
        self.failUnless('unicode_htmltext_lexicon' in ids)

    def testSearchableTextIndex(self):
        index = self.catalog._catalog.getIndex('SearchableText')
        self.failUnless(isinstance(index.getLexicon(), UnicodeLexicon))

    def testDescriptionIndex(self):
        index = self.catalog._catalog.getIndex('Description')
        self.failUnless(isinstance(index.getLexicon(), UnicodeLexicon))

    def testTitleIndex(self):
        index = self.catalog._catalog.getIndex('Title')
        self.failUnless(isinstance(index.getLexicon(), UnicodeLexicon))

    def testReimportUnicodeLexicon(self):
        self.setup.runImportStepFromProfile(
            'profile-Products.UnicodeLexicon:default', 'unicodelexicon', run_dependencies=True)
        self.testCatalogLexicons()
        self.testSearchableTextIndex()

    def testReimportAllSteps(self):
        self.setup.runAllImportStepsFromProfile('profile-Products.UnicodeLexicon:default')
        self.testCatalogLexicons()
        self.testSearchableTextIndex()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

