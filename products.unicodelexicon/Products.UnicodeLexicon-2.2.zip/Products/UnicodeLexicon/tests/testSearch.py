# -*- coding: utf-8 -*-

#
# Test indexing and searching
#

from Products.UnicodeLexicon.tests import UnicodeLexiconTestCase

from Products.UnicodeLexicon.pipeline import UnicodeLatinAccentNormalizer
from Products.UnicodeLexicon.pipeline import UnicodeStopWordRemover


class TestCaseFolding(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc1', title='Mother')
        self.folder.invokeFactory('Document', id='doc2', title='mother')

    def testSearchTitle(self):
        brains = self.catalog(Title='FATHER')
        self.assertEqual(len(brains), 0)
        brains = self.catalog(Title='MOTHER')
        self.assertEqual(len(brains), 2)

    def testSearchText(self):
        brains = self.catalog(SearchableText='FATHER')
        self.assertEqual(len(brains), 0)
        brains = self.catalog(SearchableText='MOTHER')
        self.assertEqual(len(brains), 2)


class TestAccent(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc1', title='Bon marché')
        self.folder.invokeFactory('Document', id='doc2', title='Marche pas')

    def testSearchAccent(self):
        brains = self.catalog(Title='marché')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].Title, 'Bon marché')

    def testSearchNoAccent(self):
        brains = self.catalog(Title='marche')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].Title, 'Marche pas')

    def testPhraseSearchAccent(self):
        brains = self.catalog(Title='"BON marché"')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].Title, 'Bon marché')

    def testPhraseSearchNoAccent(self):
        brains = self.catalog(Title='"BON marche"')
        self.assertEqual(len(brains), 0)


class TestAccentFolding(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        lexicon = self.catalog.unicode_plaintext_lexicon
        lexicon._pipeline = lexicon._pipeline + (UnicodeLatinAccentNormalizer(),)
        self.folder.invokeFactory('Document', id='doc1', title='Bon marché')
        self.folder.invokeFactory('Document', id='doc2', title='Marche pas')

    def testSearchAccent(self):
        brains = self.catalog(Title='marché', sort_on='getId')
        self.assertEqual(len(brains), 2)
        self.assertEqual(brains[0].Title, 'Bon marché')
        self.assertEqual(brains[1].Title, 'Marche pas')

    def testSearchNoAccent(self):
        brains = self.catalog(Title='marche', sort_on='getId')
        self.assertEqual(len(brains), 2)
        self.assertEqual(brains[0].Title, 'Bon marché')
        self.assertEqual(brains[1].Title, 'Marche pas')

    def testPhraseSearchAccent(self):
        brains = self.catalog(Title='"Bon Marché"')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].Title, 'Bon marché')

    def testPhraseSearchNoAccent(self):
        brains = self.catalog(Title='"Bon Marche"')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].Title, 'Bon marché')


class TestSearchableText(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        lexicon = self.catalog.unicode_htmltext_lexicon
        lexicon._pipeline = lexicon._pipeline + (UnicodeLatinAccentNormalizer(),)
        self.folder.invokeFactory('Document', id='doc3', text="the quick brówn fox jumps over the lazy dog")
        self.folder.invokeFactory('Document', id='doc4', text="the quick fox jumps lazy over the brown dog")

    def testSearchAccent(self):
        brains = self.catalog(SearchableText='Quick brówn fox', sort_on='getId')
        self.assertEqual(len(brains), 2)
        self.assertEqual(brains[0].getId, 'doc3')
        self.assertEqual(brains[1].getId, 'doc4')

    def testSearchNoAccent(self):
        brains = self.catalog(SearchableText='Quick brown fox', sort_on='getId')
        self.assertEqual(len(brains), 2)
        self.assertEqual(brains[0].getId, 'doc3')
        self.assertEqual(brains[1].getId, 'doc4')

    def testPhraseSearchAccent(self):
        brains = self.catalog(SearchableText='"Quick brówn fox"')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getId, 'doc3')

    def testPhraseSearchNoAccent(self):
        brains = self.catalog(SearchableText='"Quick brown fox"')
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getId, 'doc3')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCaseFolding))
    suite.addTest(makeSuite(TestAccent))
    suite.addTest(makeSuite(TestAccentFolding))
    suite.addTest(makeSuite(TestSearchableText))
    return suite

