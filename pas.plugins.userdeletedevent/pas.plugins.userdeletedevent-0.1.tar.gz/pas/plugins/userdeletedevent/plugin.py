"""
ZODB based user manager with introspection and management interfaces.
"""

from zope.interface import implements
import zope.event

from AccessControl import ClassSecurityInfo

from App.class_init import InitializeClass

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.events import PrincipalDeleted

from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PlonePAS.plugins.user import UserManager as BaseUserManager


manage_addUserDeletedEventPlugin = PageTemplateFile("./templates/addUserDeletedEventPlugin",
        globals(), __name__="manage_addUserDeletedEventPlugin")


def addUserDeletedEventPlugin(dispatcher, id, title=None, REQUEST=None):
    """ Add a UserManager to a Pluggable Auth Service. """
    pum = UserDeletedEventPlugin(id, title)
    dispatcher._setObject(pum.getId(), pum)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '%s/manage_workspace'
            '?manage_tabs_message='
            'User+Deleted+Event+Plugin+added.'
            % dispatcher.absolute_url())


class UserDeletedEventPlugin(BaseUserManager):
    """PAS plugin for managing users. (adds write API)
    """

    meta_type = 'User Manager Deleted Event'
    security = ClassSecurityInfo()
    #implements(IUserManagement)

    security.declarePrivate('doDeleteUser')
    def doDeleteUser(self, userid):
        """Given a user id, delete that user
        """
        zope.event.notify(PrincipalDeleted(userid))
        return self.removeUser(userid)

InitializeClass(UserDeletedEventPlugin)
