"""Unit tests for the installation and uninstallation"""

import os, sys
import unittest

from zope.interface import directlyProvides

from Products.PloneTestCase import PloneTestCase as ptc
from Products.CMFCore.utils import getToolByName

from plonetheme.xtheme.browser.interfaces import IThemeSpecific
from plonetheme.xtheme.tests.base import TestCase

ptc.setupPloneSite(products=['plonetheme.xtheme'])


class TestInstall(TestCase):
    """Test theme installation"""

    def afterSetUp(self):
        self.skins = getToolByName(self.portal, 'portal_skins')
        self.css = getToolByName(self.portal, 'portal_css')
        self.setup = getToolByName(self.portal, 'portal_setup')
        self.js = getToolByName(self.portal, 'portal_javascripts')
		
        # Shouldn't this happen automatically?
        directlyProvides(self.portal.REQUEST, IThemeSpecific)

    def test_theme_css_added(self):
            """Test that the main CSS file is registered"""
            resources = self.css.getResources()
            resources = dict(zip([i.getId() for i in resources], resources))
            self.failUnless('main.css' in resources)
            self.failUnless(resources['main.css'].getEnabled())

    def test_theme_js_added(self):
        """Test that the main js file is registered"""
        resources = self.js.getResources()
        resources = dict(zip([i.getId() for i in resources], resources))
        self.failUnless('++resource++plonetheme.xtheme.scripts/main.js' in resources)
        self.failUnless(resources['++resource++plonetheme.xtheme.scripts/main.js'].getEnabled())
    
    def test_skin_selection_added(self):
           """Check that 'XTheme Theme' is in portal_skins"""
           self.failUnless('XTheme Theme' in self.skins.getSkinSelections())
 
    def test_default_skin_selection(self):
        """Check that 'Xtheme Theme' is the default skin"""
        self.assertEqual(self.skins.getDefaultSkin(), 'XTheme Theme')

    def test_personal_bar_moved_to_footer(self):
        """Check that personal bar is in the footer viewlet manager"""
        site_actions_in_footer = self.is_viewlet_in_viewlet_manager(
            'plone.personal_bar',
            'plone.portalfooter')
        self.failUnless(site_actions_in_footer)

        site_actions_hidden_in_portaltop = self.is_hidden_viewlet(
            'plone.personal_bar',
            'plone.portaltop',
        )
        self.failIf(site_actions_hidden_in_portaltop)
 
    def test_path_bar_is_hidden(self):
        """Check that the path bar is hidden"""
        path_bar_hidden_in_portaltop = self.is_hidden_viewlet(
            'plone.path_bar',
            'plone.portaltop',
        )
        self.failIf(path_bar_hidden_in_portaltop)

    def test_search_box_is_hidden(self):
        """Check that the search box is hidden"""
        search_box_hidden_in_header = self.is_hidden_viewlet(
            'plone.search_box',
            'plone.portalheader',
        )
        self.failIf(search_box_hidden_in_header)

    def test_footer_viewlets_order(self):
        """Test order of viewlets in the footer viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portalfooter')
        target_order = (
            u'plone.personal_bar',
            u'plone.footer',
            u'plone.colophon',
			u'plone.analytics',
        )
        self.assertEquals(viewlets, target_order)

class TestUninstall(TestCase):
    """Test theme uninstalation"""

    def afterSetUp(self):
        self.skins = getToolByName(self.portal, 'portal_skins')
        self.css = getToolByName(self.portal, 'portal_css')
        self.setup = getToolByName(self.portal, 'portal_setup')
        self.js = getToolByName(self.portal, 'portal_javascripts')

        uninstall_profile = 'profile-plonetheme.xtheme:uninstall'
        self.setup.runAllImportStepsFromProfile(uninstall_profile)

    def test_theme_css_removed(self):
        """Test that the main CSS file is not registered"""
        resources = self.css.getResources()
        resources = dict(zip([i.getId() for i in resources], resources))
        self.failIf('main.css' in resources)

    def test_theme_js_added(self):
        """Test that the main js file is registered"""
        resources = self.js.getResources()
        resources = dict(zip([i.getId() for i in resources], resources))
        self.failIf('++resource++plonetheme.xtheme.scripts/main.js' in resources)

    def test_skin_selection_removed(self):
        """Check that 'XTheme Theme' is not in portal_skins"""
        self.failIf('XTheme Theme' in self.skins.getSkinSelections())
 
    def test_default_skin_selection(self):
        """Check that 'XTheme Theme' is not the default skin"""
        self.failIf(self.skins.getDefaultSkin() == 'XTheme Theme')

    def test_personal_bar_moved_to_top(self):
        """Check that personal bar is in the top viewlet manager"""
        personal_bar_in_footer = self.is_viewlet_in_viewlet_manager(
            'plone.personal_bar',
            'plone.portalfooter')
        self.failIf(personal_bar_in_footer)

        personal_bar_in_top = self.is_viewlet_in_viewlet_manager(
            'plone.personal_bar',
            'plone.portalheader')
        self.failUnless(personal_bar_in_top)

    def test_path_bar_in_abovecontent(self):
        """Check that the path bar is in the top viewlet
        manager
        """
        path_bar_in_top = self.is_viewlet_in_viewlet_manager(
            'plone.path_bar',
            'plone.abovecontent')
        self.failUnless(path_bar_in_top)

    def test_search_box_moved_to_top(self):
        """Check that the searchbox is in the header viewlet
        manager
        """
        searchbox_in_header = self.is_viewlet_in_viewlet_manager(
            'plone.searchbox',
            'plone.portalheader')
        self.failUnless(searchbox_in_header)


    def test_footer_viewlets_order(self):
        """Test order of viewlets in the footer viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portalfooter')
        target_order = (
            u'plone.footer',
            u'plone.colophon',
            u'plone.site_actions',
        )
        self.assertEquals(viewlets, target_order)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstall))
    suite.addTest(unittest.makeSuite(TestUninstall))
    return suite

