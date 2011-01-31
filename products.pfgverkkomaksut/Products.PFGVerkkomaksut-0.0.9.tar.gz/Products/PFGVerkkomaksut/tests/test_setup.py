import unittest
from Products.CMFCore.utils import getToolByName
from Products.PFGVerkkomaksut.tests.base import PFGVerkkomaksutTestCase

class TestSetup(PFGVerkkomaksutTestCase):

    def afterSetUp(self):
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.types = getToolByName(self.portal, 'portal_types')
        self.wftool = getToolByName(self.portal, 'portal_workflow')
        self.content_types = [
            'PFGVerkkomaksut',
        ]
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.skins      = getToolByName(self.portal, 'portal_skins')

    def test_is_pfg_installed(self):
        self.failUnless(self.installer.isProductInstalled('PloneFormGen'))

    def test_is_pfg_verkkomaksut_installed(self):
        self.failUnless(self.installer.isProductInstalled('PFGVerkkomaksut'))

    def testSkinLayersInstalled(self):
        self.failUnless('PFGVerkkomaksut' in self.skins.objectIds())

    ## Content Types
    def test_contents_installed(self):
        for type in self.content_types:
            self.failUnless(type in self.types.objectIds())

    # Workflow
    def test_workflow_mapped(self):
        for portal_type, chain in self.wftool.listChainOverrides():
            if portal_type in ('PFGVerkkomaksut'):
                self.assertEquals((), chain)
            if portal_type in ('File', 'Image'):
                self.assertEquals((), chain)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
