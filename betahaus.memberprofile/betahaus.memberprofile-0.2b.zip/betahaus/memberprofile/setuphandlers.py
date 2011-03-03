import logging
logger = logging.getLogger('betahaus.memberprofile: setuphandlers')

from Products.CMFCore.utils import getToolByName

def profile_default(context):
    if context.readDataFile('memberprofile_marker.txt') is None:
        return
    """Run by the default profile"""
    setup = Setup(context)
    setup.setup_member_folders_type('MemberProfile')
    setup.portal_membership.memberareaCreationFlag = 1
    #setup.disable_memberareas()

class Setup:
    """ Setup methods for betahaus.memberprofile """
    
    def __init__(self, context):
        """ Initialize and add common varaibles """
        #Common tools etc.
        self.portal = context.getSite()
        self.portal_membership = getToolByName(self.portal, 'portal_membership')
    
    def setup_member_folders_type(self, type):
        """Turn creation on and set type to MemberProfile"""
        self.portal_membership.memberarea_type = type

        # make sure that the type is both linkable and registered as a container, so that you can 
        # link to stuff inside a MemberProfile
        #Note: TinyMCE settings are imported from the regular Generic Setup profile

        #Note: Kupu linkable types stopped working in 3.3.5
        #Since Plone 3 isn't very actively maintained, I'm not
        #going to fix it here either. It can be added manually from the controlpanel                                      


    def disable_memberareas(self):
        """ Don't create member areas the Plone way. """
        #FIXME: We should remove the option from the control panel if we can :/
        self.portal_membership.memberareaCreationFlag = 0
