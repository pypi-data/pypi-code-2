# -*- coding: utf-8 -*-
"""
test_setup.py - test installation of niteoweb.clickbank into Plone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""

import unittest

from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError

from Products.CMFCore.utils import getToolByName

from niteoweb.clickbank.interfaces import IClickBankSettings
from niteoweb.clickbank.tests import ClickBankIntegrationTestCase

class TestInstall(ClickBankIntegrationTestCase):
    """Test installation of niteoweb.clickbank into Plone."""
        
    def test_disable_registration_for_anonymous(self):
        """Test if anonymous visitors are prevented to register to the site."""
        # The API of the permissionsOfRole() function sucks - it is bound too
        # closely up in the permission management screen's user interface
        self.failIf('Add portal member' in [r['name'] for r in 
                                self.portal.permissionsOfRole('Anonymous') if r['selected']])

    def test_clickbank_fields_added(self):
        """Test if ClickBank-specific fields were added to memberdata."""
        properties = self.portal.portal_memberdata.propertyIds()
        self.failUnless('product_id' in properties)
        self.failUnless('affiliate' in properties)
        self.failUnless('last_purchase_id' in properties)        
        self.failUnless('last_purchase_timestamp' in properties)
    
    def test_use_email_as_login(self):
        """Test if email is indeed used as username."""
        site_properties = self.portal.portal_properties.site_properties
        self.failUnless(site_properties.getProperty('use_email_as_login') == True)
        
    def test_control_panel_configlet_accessible(self):
        """Test if the 'Configure ClickBank' control panel configlet can be accessed."""
        view = getMultiAdapter((self.portal, self.portal.REQUEST), name="configure-clickbank")
        view = view.__of__(self.portal)
        self.failUnless(view())

class TestUninstall(ClickBankIntegrationTestCase):
    """Test un-installation of niteoweb.clickbank from Plone."""
        
    def afterSetUp(self):
        """ Grab the skins, css and js tools and uninstall NuPlone. """
        quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        quickinstaller.uninstallProducts(products=["niteoweb.clickbank"])

    def test_product_uninstalled(self):
        """Test if the product was uninstalled."""
        quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.failIf(quickinstaller.isProductInstalled("niteoweb.clickbank"))

    def test_local_utility_removed(self):
        """Test if the IClickBankSettings local utility was removed."""
        try:
            getUtility(IClickBankSettings)
        except ComponentLookupError:
            pass
    
    def test_control_panel_configlet_removed(self):
        """Test if the 'Configure ClickBank' control panel configlet was removed."""
        view = getMultiAdapter((self.portal, self.portal.REQUEST), name="configure-clickbank")
        view = view.__of__(self.portal)
        try:
            self.failIf(view())
        except TypeError:
            pass
          
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstall))
    suite.addTest(unittest.makeSuite(TestUninstall))
    return suite
