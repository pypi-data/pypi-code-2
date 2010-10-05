from zope.interface import implements
from Solgema.fullcalendar.interfaces import ISolgemaFullcalendarEditableFilter
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

class SolgemaFullcalendarEditableFilter(object):

    implements(ISolgemaFullcalendarEditableFilter)

    def __init__(self, context):
        self.context = context

    def _listSFAllowedRolesAndUsersModify(self):
        sm = getSecurityManager()
        user = sm.getUser()
        effective_roles = user.getRoles()
        if sm.calledByExecutable():
            eo = sm._context.stack[-1]
            proxy_roles = getattr(eo, '_proxy_roles', None)
            if proxy_roles is not None:
                effective_roles = proxy_roles
        result = list( effective_roles )
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
        return result

    def filterEvents(self, args):
        editargs = args.copy()
        catalog = getToolByName(self.context, 'portal_catalog')
        editargs['SFAllowedRolesAndUsersModify'] = self._listSFAllowedRolesAndUsersModify()
        return [a.getURL() for a in catalog.searchResults(**editargs)]

