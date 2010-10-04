import unittest

from zope.component import getSiteManager
from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase
from collective.salesforce.rsvp.config import PROJECTNAME
from collective.salesforce.rsvp import interfaces
from collective.salesforce.rsvp.helpers import uninstallVarious

from Products.PloneTestCase import PloneTestCase
default_user = PloneTestCase.default_user

class TestRSVPUninstallation(SFRSVPTestCase):
    """Test suite ensures that we're playing nice
       and cleaning up nicely upon uninstallation
    """
    def _uninstall_product(self):
        # uninstall our product for test suite
        if self.qi.isProductInstalled(PROJECTNAME):
            self.setRoles(['Manager',])
            # official uninstall
            self.qi.uninstallProducts([PROJECTNAME,])
            
            # XXX this isn't currently available via any Plone-centric 
            # UI. It's more a demonstration of the bits and pieces
            # that were configured via GenericSetup and currently aren't 
            # handled by the quick installer and it's installed product
            # as new releases of the CMFQuickInstallerTool handle other
            # areas of generic setup profile rollback this can be removed.
            uninstallVarious(self.portal)
            
            self.login(default_user)
    
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.actions = getToolByName(self.portal, 'portal_actions')
        self.action_icons = getToolByName(self.portal, 'portal_actionicons')
        self.kss = getToolByName(self.portal, 'portal_kss')
        self.portal_setup = getToolByName(self.portal, 'portal_setup')
    
    def test_product_newly_installable_after_uninstall(self):
        self._uninstall_product()
        self.failIf(self.qi.isProductInstalled(PROJECTNAME))
        self.failUnless(self.qi.isProductInstallable(PROJECTNAME))
    
    def test_component_registry(self):
        self._uninstall_product()
        sm = getSiteManager(self.portal)
        registered_adapters = [r.name for r in sm.registeredAdapters()]
        self.failIf(u"sfcollective.salesforce.rsvp_adapter" in registered_adapters)
    
    def test_action_deconfiguration(self):
        self._uninstall_product()
        # make sure enable rsvps was removed as an object_buttons
        self.failIf(hasattr(self.actions.object_buttons, 'allowRSVPs'))
        
        # make sure disable rsvps was removed as an object_buttons
        self.failIf(hasattr(self.actions.object_buttons, 'disableRSVPs'))
    
    def test_action_icon_deconfiguration(self):
        self._uninstall_product()
        for act_icon in ('allowRSVPs','disableRSVPs',):
            self.assertRaises(KeyError, self.action_icons.getActionIcon, 'object_buttons', act_icon,
                "Action icon %s doesn't raise KeyError, must still exist upon uninstall" % act_icon)
    
    def test_kss_unregistration(self):
        self._uninstall_product()
        # self.kss.manage_removeKineticStylesheet('++resource++rsvp.kss')
        
        # confirm kinetic stylesheet registration
        for kss_id in ('++resource++rsvp.kss',):
            self.failIf(kss_id in self.kss.getResourceIds(),
                "The kss resource %s exists in the the portal_kss registry after uninstallation")
    
    def test_rsvpable_interface_no_longer_provided(self):
        # when we run our uninstall profile and get rid of
        # the rsvp adapter providing ISchemaExtender for
        # items marked with the ISalesforceRSVPable interface
        # we have major problems.  This makes sure that those
        # items no longer provide the interface
        
        # we make several rsvpable objects to interact with
        for i in range(3):
            self.folder.invokeFactory("Event", 'rsvpable%s' % i)
            # apply the marker interface to our event object
            alsoProvides(self.folder["rsvpable%s" % i], interfaces.ISalesforceRSVPable)
            # reindex the object so it's findable via the catalog
            self.folder["rsvpable%s" % i].reindexObject(idxs=['object_provides',])
        
        # start the uninstall process
        self._uninstall_product()
        
        # no we ensure that all those items that once 
        # provided ISalesforceRSVPable no longer do
        for i in range(3):
            self.failIf(interfaces.ISalesforceRSVPable.providedBy(self.folder["rsvpable%s" % i]))
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRSVPUninstallation))
    return suite
