"""Unit tests for the installation and uninstallation"""

import os, sys
import unittest

from zope.interface import directlyProvides

from Products.PloneTestCase import PloneTestCase as ptc
from Products.CMFCore.utils import getToolByName

from plonetheme.keepitsimple.browser.interfaces import IThemeSpecific
from plonetheme.keepitsimple.tests.base import TestCase

ptc.setupPloneSite(products=['plonetheme.keepitsimple'])


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

    def test_skin_selection_added(self):
        """Check that 'Keep it Simple' is in portal_skins"""
        self.failUnless('Keep it Simple' in self.skins.getSkinSelections())

    def test_default_skin_selection(self):
        """Check that 'Keep it Simple' is the default skin"""
        self.assertEqual(self.skins.getDefaultSkin(), 'Keep it Simple')

    def test_personal_bar_moved_to_top(self):
       """Check that personal bar is in the top viewlet manager"""
       site_actions_in_top = self.is_viewlet_in_viewlet_manager(
           'plone.personal_bar',
           'plone.portaltop')
       self.failUnless(site_actions_in_top)

       site_actions_hidden_in_portalheader = self.is_hidden_viewlet(
           'plone.personal_bar',
           'plone.portalheader',
       )
       self.failIf(site_actions_hidden_in_portalheader)

    def test_logo_moved_to_intro(self):
        """Check that the logo is in the intro viewlet manager"""
        logo_in_intro = self.is_viewlet_in_viewlet_manager(
            'plone.logo',
            'plone.portalintro')
        self.failUnless(logo_in_intro)

    def test_plone_logo_is_hidden(self):
        """Check that the plone logo is hidden"""
        plone_logo_hidden_in_portalheader = self.is_hidden_viewlet(
            'plone.logo',
            'plone.portalheader',
        )
        self.failIf(plone_logo_hidden_in_portalheader)

    def test_site_actions_is_hidden_in_footer(self):
        """Check that the site_actions are hidden in the footer"""
        site_actions_in_portalfooter = self.is_hidden_viewlet(
            'plone.site_actions',
            'plone.portalfooter',
        )
        self.failIf(site_actions_in_portalfooter)

    def test_header_viewlets_order(self):
        """Test order of viewlets in the header viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portalheader')
        target_order = (
            u'plone.skip_links',
            u'plone.searchbox',
            u'plone.global_sections',
            u'plone.logo',
            u'plone.intro',
        )
        self.assertEquals(viewlets, target_order)

    def test_top_viewlets_order(self):
        """Test order of viewlets in the top viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portaltop')
        target_order = (
            u'plone.header',
            u'plone.app.i18n.locales.languageselector',
            u'plone.personal_bar',
            u'plone.path_bar',
        )
        self.assertEquals(viewlets, target_order)

    def test_intro_viewlets_order(self):
        """Test order of viewlets in the intro viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portalintro')
        target_order = (
            u'plone.logo',
            u'plone.introtext',
        )
        self.assertEquals(viewlets, target_order)


class TestUninstall(TestCase):
    """Test theme uninstalation"""

    def afterSetUp(self):
        self.skins = getToolByName(self.portal, 'portal_skins')
        self.css = getToolByName(self.portal, 'portal_css')
        self.setup = getToolByName(self.portal, 'portal_setup')

        uninstall_profile = 'profile-plonetheme.keepitsimple:uninstall'
        self.setup.runAllImportStepsFromProfile(uninstall_profile)

    def test_theme_css_removed(self):
        """Test that the main CSS file is not registered"""
        resources = self.css.getResources()
        resources = dict(zip([i.getId() for i in resources], resources))
        self.failIf('main.css' in resources)

    def test_skin_selection_removed(self):
        """Check that 'Keep it Simple' is not in portal_skins"""
        self.failIf('Keep it Simple' in self.skins.getSkinSelections())

    def test_default_skin_selection(self):
        """Check that 'Keep it Simple' is not the default skin"""
        self.failIf(self.skins.getDefaultSkin() == 'Keep it Simple')


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

