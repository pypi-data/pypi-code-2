from zope.i18nmessageid import MessageFactory

from Products.Five.browser import BrowserView
from plone.stringinterp.adapters import _recursiveGetMembersFromIds
from Products.CMFCore.utils import getToolByName

PMF = MessageFactory('plone')

from collective.local.userlisting.interfaces import IUserListingAvailable

class Expressions(BrowserView):

    def userlisting_available(self):
        return IUserListingAvailable.providedBy(self.context)

ROLES = ['Site Administrator',
         'Reviewer',
         'Editor',
         'Contributor',
         'Reader']

def recursive_users_with_local_role(content, portal, role):
    # union with set of ids of members with the local role
    users_with_local_role = content.users_with_local_role(role)
    return _recursiveGetMembersFromIds(portal, users_with_local_role)


class View(BrowserView):

    def users_by_role(self):
        """a list of dictionnaries
            {'role': message,
             'users': list of users}
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        site_url = portal.absolute_url()
        infos = []

        for role in ROLES:
            users = recursive_users_with_local_role(self.context, portal, role)
            if len(users) == 0:
                continue

            role_infos = {'role': PMF(role)}
            role_infos['users'] = []
            for user in users:
                user_id = user.getUserName()
                user_infos = {'id': user_id,
                              'fullname': user.getProperty('fullname') or user_id,
                              'home': "%s/author/%s" % (site_url, user_id),
                              'email': user.getProperty('email'),
                              }
                role_infos['users'].append(user_infos)

            infos.append(role_infos)

        return infos