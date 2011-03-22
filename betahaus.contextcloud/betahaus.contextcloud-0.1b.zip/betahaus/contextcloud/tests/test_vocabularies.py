import unittest

from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.PloneTestCase.ptc import PloneTestCase

from betahaus.contextcloud.tests.layer import ContextCloudLayer


class TestVocabs(PloneTestCase):
 
    layer = ContextCloudLayer
    
    def afterSetUp(self):
        pass
        #self.loginAsPortalOwner()

    def test_query_selectable_indexes(self):
        self.failUnless(queryUtility(IVocabularyFactory, "betahaus.contextcloud.SelectableCatalogIndexes"))

    def test_query_layouts(self):
        self.failUnless(queryUtility(IVocabularyFactory, "betahaus.contextcloud.SelectableLayouts"))

    def test_index_values(self):
        vocabs = queryUtility(IVocabularyFactory, "betahaus.contextcloud.SelectableCatalogIndexes")
        self.failUnless('Subject' in [x.title for x in vocabs(self.portal)])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)