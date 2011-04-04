from unittest import TestSuite
from Products.CMFCore.utils import getToolByName

from collective.types.externalsearch.tests.base import TypesTestCase

def isProductInstallable(quickInstaller, productName):
    """Does this product show up in the quickinstaller
    list of products that are installable?

    Returns True or False
    """
    productList = quickInstaller.listInstallableProducts(skipInstalled=False)
    return productName in [x['id'] for x in productList]

class TestSetupTypes(TypesTestCase):
    """Make sure we can install types, etc.
    """

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')

    def testSetup(self):
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        #Make sure product is installable via the quick installer
        self.assertTrue(isProductInstallable(qi,
                                             'collective.types.externalsearch'),
                        'collective.types.externalsearch is not installable')

        #Make sure the product is installed
        self.assertTrue(qi.isProductInstalled('collective.types.externalsearch'),
                        'collective.types.externalsearch installation failed')
        
    def test_types_versioned(self):
        """Make sure the types are versioned.
        I put this here instead of in policy because I want
        the types versioned no matter which policy is used.
        """
        repository = getToolByName(self.portal,
                                   'portal_repository')
        versionable = repository.getVersionableContentTypes()
        for type_id in ('collective.types.ExternalSearch',):
            self.failUnless(type_id in versionable,
                            '%s is not versionable' % type_id)

    def test_type_installed(self):
        self.failUnless('collective.types.ExternalSearch' in
                        self.types.objectIds(),
                        'The ExternalSearch type is not installed')


def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSetupTypes))

    return suite

