#
# Test lexicon default encoding override
#

from Products.UnicodeLexicon.tests import UnicodeLexiconTestCase
from Products.UnicodeLexicon.interfaces import IDefaultEncoding

from zope.component import getGlobalSiteManager
from zope.component import queryUtility
from Products.Five import zcml

from Products.UnicodeLexicon.pipeline import getDefaultEncoding
testEncoding = 'latin-2'


class TestDefaultEncoding(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def beforeTearDown(self):
        getGlobalSiteManager().unregisterUtility(None, IDefaultEncoding)

    def testMissingUtility(self):
        self.assertEqual(queryUtility(IDefaultEncoding), None)

    def testUtility(self):
        zcml.load_string("""
        <configure xmlns="http://namespaces.zope.org/zope">
          <utility
              provides="Products.UnicodeLexicon.interfaces.IDefaultEncoding"
              component="Products.UnicodeLexicon.pipeline.defaultEncoding"
              />
        </configure>
        """)
        self.assertEqual(queryUtility(IDefaultEncoding), 'utf-8')

    def testGetDefaultEncoding(self):
        self.assertEqual(getDefaultEncoding(), 'utf-8')

    def testGetCustomEncoding(self):
        zcml.load_string("""
        <configure xmlns="http://namespaces.zope.org/zope">
          <utility
              provides="Products.UnicodeLexicon.interfaces.IDefaultEncoding"
              component="Products.UnicodeLexicon.tests.testDefaultEncoding.testEncoding"
              />
        </configure>
        """)
        self.assertEqual(getDefaultEncoding(), 'latin-2')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultEncoding))
    return suite

