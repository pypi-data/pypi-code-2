from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class LastLogin(BrowserView):

    def memberinfo(self):
        mtool = getToolByName(self.context, 'portal_membership')
        for user in mtool.searchForMembers():
            yield({'id': user.getId(),
                   'login_time': user.getProperty('login_time'),
                   'last_login_time': user.getProperty('last_login_time'),
                   })
