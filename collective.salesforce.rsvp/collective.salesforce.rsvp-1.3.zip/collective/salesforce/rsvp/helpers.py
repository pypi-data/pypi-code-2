"""
RSVP for Salesforce uninstall helpers
"""
from zope.component import getSiteManager

from Products.CMFCore.utils import getToolByName

from archetypes.schemaextender.interfaces import ISchemaExtender

from collective.salesforce.rsvp.rsvpable import RSVPExtender
from collective.salesforce.rsvp import interfaces

class RSVPUninstall:
    def remove_kss_resources(self, p):
        kss_reg = getToolByName(p, 'portal_kss')
        kss_reg.manage_removeKineticStylesheet('++resource++rsvp.kss')
        
    def remove_named_adapter(self, p):
        sm = getSiteManager(p)
        sm.unregisterAdapter(factory=RSVPExtender,
                             required=None,
                             provided=ISchemaExtender,
                             name=u"sfcollective.salesforce.rsvp_adapter")
    
    def remove_action_icons(self, p):
        action_icons = getToolByName(p, 'portal_actionicons')
        
        for act_icon in ('allowRSVPs', 'disableRSVPs',):
            if action_icons.getActionIcon('object_buttons', act_icon):
                action_icons.removeActionIcon('object_buttons', act_icon)
    
    def disable_rsvp_marker_interface(self, p):
        # get the relevant objects via the object_provides index
        cat = getToolByName(p, 'portal_catalog')
        rsvpable_items = cat.searchResults(
            object_provides = interfaces.ISalesforceRSVPable.__identifier__)
        
        for r in rsvpable_items:
            # get the object
            r_obj = r.getObject()
            # make sure there's no catalog mismatch
            if interfaces.ISalesforceRSVPable.providedBy(r_obj):
                # just in case we end up doing more to enable/disable
                # or the api changes, we get our configuration view
                # and then disable rsvps
                r_config = r_obj.restrictedTraverse("@@rsvp-configuration")
                r_config.disableRSVPs()
    



def uninstallVarious(site):
    """
    Uninstall various settings.

    Handler that removes pieces of initial profile installation
    not yet handled by CMFQuickInstallerTool
    """
    uninstall_helper = RSVPUninstall()
    uninstall_helper.remove_kss_resources(site)
    uninstall_helper.remove_named_adapter(site)
    uninstall_helper.remove_action_icons(site)
    uninstall_helper.disable_rsvp_marker_interface(site)
    
    

