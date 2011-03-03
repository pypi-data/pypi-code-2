from zope.interface import implements
from zope.event import notify
from AccessControl import ModuleSecurityInfo, allow_module, allow_class
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from betahaus.memberprofile.interfaces import IProfileUtils, IProfileComplete,\
    IMemberProfileSettingsAdapter
from zExceptions import NotFound
from zope.exceptions.interfaces import UserError

class ProfileUtils(object):
    """ Utility to handle member profiles.
    """
    implements(IProfileUtils)
    __allow_access_to_unprotected_subobjects__ = 1
    
    def create(self, context):
        """ Create a home folder for the user with the user id 'user', if it doesn't exist.
            context doesn't have to be the context where it should be created.
        """
        pm = getToolByName(context, 'portal_membership')
        user = pm.getAuthenticatedMember().getId()
        if not user:
            raise UserError('Could not find username for authenticated user..')
        
        if pm.getHomeFolder():
            # This should not trigger an exception, everything is as it should.
            return False
        
        memfolder = pm.getMembersFolder()
        #Make sure members folder exists and the current user doesn't have a folder there yet
        if memfolder == None:
            raise NotFound, ("Could not find the membersFolder to create memberprofiles. "\
                             "Check that the folder exists that is defined in portal_membership")

        if shasattr(memfolder, user):
            return False
        
        #FIXME: Double-check id with pm tool
        _createObjectByType(pm.memberarea_type, memfolder, id=user)
        userfolder = getattr(memfolder, user)
        userfolder.unmarkCreationFlag()
        
        # tell everyone that this s created
        notify(ObjectInitializedEvent(userfolder))
        
        fullname = pm.getMemberInfo()['fullname']

        if fullname:
            self.set_name(fullname, userfolder)


    def set_name(self, fullname, userfolder):
        """ Set name for user """
        userfolder.setFullname(fullname)
        parts = fullname.split()
        if len(parts) == 1:
            userfolder.setFirstname(parts[0])
        if len(parts) > 1:
            userfolder.setFirstname(parts[0])
            userfolder.setLastname(' '.join(parts[1:]))
        
        userfolder.reindexObject()
    
    def is_complete_profile(self, context):
        """ checks if the profile is complete or needs more information"""
        purl = getToolByName(context, 'portal_url')
        settings = IMemberProfileSettingsAdapter(purl.getPortalObject())
        if settings.get('enforce_complete_profile'):
            return IProfileComplete(context).is_complete()
        return True
        

profileutils = ProfileUtils()

ModuleSecurityInfo('betahaus.memberprofile.utilities').declarePublic('profileutils')
allow_class(profileutils)
