import logging
logger = logging.getLogger('betahaus.memberprofile: setuphandlers')

from Products.CMFCore.utils import getToolByName

def profile_default(context):
    if context.readDataFile('memberprofile_marker.txt') is None:
        return
    """Run by the default profile"""
    setup = Setup(context)
    setup.set_member_folders_type(u'MemberProfile')
    setup.disable_member_folders()

class Setup:
    """ Setup methods for betahaus.memberprofile """
    
    def __init__(self, context):
        """ Initialize and add common varaibles """
        #Common tools etc.
        self.portal = context.getSite()
        self.portal_membership = getToolByName(self.portal, 'portal_membership')
#        self.portal_actions = getToolByName(self.portal, 'portal_actions')
#        self.quick_installer = getToolByName(self.portal, 'portal_quickinstaller')
    
    def set_member_folders_type(self, type):
        """Turn creation on and set type to MemberProfile"""
        self.portal_membership.memberarea_type = type

        # make sure that the type is both linkable and registered as a container, so that you can 
        # link to stuff inside a MemberProfile
        kupu_tool = getToolByName(self.portal, 'kupu_library_tool', None)
        if kupu_tool != None:
            linkable = list(kupu_tool.getPortalTypesForResourceType('linkable'))
            collections =  list(kupu_tool.getPortalTypesForResourceType('collection'))
            if type not in linkable:
                linkable.append(type)
            if type not in collections:
                collections.append(type)
            # kupu_library_tool has an idiotic interface, basically written purely to
            # work with its configuration page. :-(
            kupu_tool.updateResourceTypes(({'resource_type' : 'linkable',
                                           'old_type'      : 'linkable',
                                           'portal_types'  :  linkable},
                                          {'resource_type' : 'collection',
                                           'old_type'      : 'collection',
                                           'portal_types'  :  collections},))                                           

    def disable_member_folders(self):
        self.portal_membership.memberareaCreationFlag = 0
