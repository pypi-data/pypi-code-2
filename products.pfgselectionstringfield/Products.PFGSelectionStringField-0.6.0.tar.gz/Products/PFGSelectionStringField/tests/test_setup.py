import unittest
from Products.CMFCore.utils import getToolByName
from Products.PFGSelectionStringField.tests.base import PFGSelectionStringFieldTestCase

class TestSetup(PFGSelectionStringFieldTestCase):

    def afterSetUp(self):
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.types = getToolByName(self.portal, 'portal_types')
        self.wftool = getToolByName(self.portal, 'portal_workflow')
        self.content_types = [
            'PFGSelectionStringField',
        ]
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.skins      = getToolByName(self.portal, 'portal_skins')

    def test_is_pfg_installed(self):
        self.failUnless(self.installer.isProductInstalled('PloneFormGen'))

    def test_is_pfg_selection_string_field_installed(self):
        self.failUnless(self.installer.isProductInstalled('PFGSelectionStringField'))

    def testSkinLayersInstalled(self):
        self.failUnless('PFGSelectionStringField' in self.skins.objectIds())

    ## Content Types
    def test_contents_installed(self):
        for type in self.content_types:
            self.failUnless(type in self.types.objectIds())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
