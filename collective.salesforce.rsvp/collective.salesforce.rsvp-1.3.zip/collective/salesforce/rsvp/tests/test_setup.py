import unittest

from zope.interface import alsoProvides
from zope.component import getSiteManager, getUtility

from Products.CMFCore.utils import getToolByName
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase
from collective.salesforce.rsvp import interfaces
from collective.salesforce.rsvp.config import PROJECTNAME

class TestRSVPInstallation(SFRSVPTestCase):
    
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.actions = getToolByName(self.portal, 'portal_actions')
        self.action_icons = getToolByName(self.portal, 'portal_actionicons')
        self.kss = getToolByName(self.portal, 'portal_kss')
    
    def test_product_installable(self):
        self.failUnless(self.qi.isProductInstallable(PROJECTNAME))
    
    def test_product_installed(self):
        self.failUnless(self.qi.isProductInstalled(PROJECTNAME))
        
    def test_component_registry(self):
        sm = getSiteManager(self.portal)
        registered_adapters = [r.name for r in sm.registeredAdapters()]
        self.failUnless("sfcollective.salesforce.rsvp_adapter" in registered_adapters)
    
    def test_action_configuration(self):
        # make sure enable rsvps exists and is visible
        self.failUnless(self.actions.object_buttons.allowRSVPs.visible)
        
        # make sure disable rsvps exists and is visible
        self.failUnless(self.actions.object_buttons.disableRSVPs.visible)
    
    def test_action_icon_configuration(self):
        for act_icon in ('allowRSVPs','disableRSVPs',):
            self.failUnless(self.action_icons.getActionIcon('object_buttons', act_icon),
                "The action icon %s is missing from the object_buttons category" % act_icon)
    
    def test_viewlet_content_provider_registered(self):
        # we test the registration of a viewlet named rsvp.register within the
        # plone.app.layout.viewlets.interfaces.IBelowContentBody viewlet manager
        # this is not done via the more obvious (I would think) API of:
        # getSiteManager(self.portal).getUtility(IViewletSettingsStorage).getOrder('name', skinname)
        # since this only returns the "known ones" (see comment in ManageViewlet._getOrder) --
        # i.e. the viewlet managers registered by CMFPlone's GSXML.
        # Rather, ManageViewlet._getOrder queries for an IContentProvider manager
        # and gets the viewlets from there.
        
        # add an event for use, apply the marker interface
        self.folder.invokeFactory("Event", 'rsvpable')
        alsoProvides(self.folder.rsvpable, interfaces.ISalesforceRSVPable)
        
        self.setRoles(['Manager',])
        self.failIf('rsvp.register' in 
            self.portal['front-page'].restrictedTraverse('@@manage-viewlets')._getOrder('plone.belowcontentbody'))
        
        self.failUnless('rsvp.register' in 
            self.folder.rsvpable.restrictedTraverse('@@manage-viewlets')._getOrder('plone.belowcontentbody'))
    
    def test_viewlet_content_provider_ordering(self):
        # we want to push our rsvp form up to the top of the plone.belowcontentbody
        # provider, so it looks tacked right onto the end of the content.
        self.folder.invokeFactory("Event", 'rsvpable')
        alsoProvides(self.folder.rsvpable, interfaces.ISalesforceRSVPable)
        
        self.setRoles(['Manager',])
        viewlet_manager = self.folder.rsvpable.restrictedTraverse('@@manage-viewlets')
        self.assertEqual(0, viewlet_manager._getOrder('plone.belowcontentbody').index('rsvp.register'))
    
    def test_kss_registration(self):
        # confirm kinetic stylesheet registration
        for kss_id in ('++resource++rsvp.kss',):
            self.failUnless(kss_id in self.kss.getResourceIds(),
                "The kss resource %s wasn't registered appropriately with the portal_kss registry")
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRSVPInstallation))
    return suite
