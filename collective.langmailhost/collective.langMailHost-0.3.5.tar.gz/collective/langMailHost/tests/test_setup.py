import unittest
from Products.CMFCore.utils import getToolByName
from collective.langMailHost.tests.base import MailHostTestCase

class TestSetup(MailHostTestCase):

    def afterSetUp(self):
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.properties = getToolByName(self.portal, 'portal_properties')
        self.skins = getToolByName(self.portal, 'portal_skins')

    def test_is_langMailHost_installed(self):
        self.failUnless(self.installer.isProductInstalled('collective.langMailHost'))

    ## Propertiestool.xml
    def test_lang_charset(self):
        self.failUnless('ja|iso-2022-jp', self.properties.mailhost_properties.getProperty('lang_charset'))

    def test_is_member_lang_effective(self):
        self.assertEquals(True, self.properties.mailhost_properties.getProperty('is_member_lang_effective'))

#    def test_is_site_lang_effective(self):
#        self.assertEquals(True, self.properties.mailhost_properties.getProperty('is_site_lang_effective'))

    ## skins.xml
    def test_skin(self):
        layer = self.skins.getSkinPath(self.skins.getDefaultSkin())
        self.failUnless('collective_langMailHost_scripts' in layer)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
