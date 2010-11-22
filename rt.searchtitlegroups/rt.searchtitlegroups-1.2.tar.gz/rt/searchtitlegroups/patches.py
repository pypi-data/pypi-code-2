from Products.PluggableAuthService.plugins.ZODBGroupManager import ZODBGroupManager
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

def updateGroup(self, group_id, title=None, description=None):
    """
    This one is fixed in Products.PlonePAS 4.x (in plone 4.x)
    @author: mirco
    """
    ZODBGroupManager.updateGroup(self, group_id, title=title, description=description)
    return True

def group_search_results(self):
        """
        Use of our custom function (searchGroups) to search in titles and ids of groups
        @author: mirco
        """
        def search_for_principal(hunter, search_term):
            search_view = getMultiAdapter((hunter, hunter.request), name='adv_search_groups')
            return search_view.searchGroups(search_term)
        
        def get_principal_by_id(group_id):
            portal_groups = getToolByName(self.context, 'portal_groups')
            return portal_groups.getGroupById(group_id)
        
        def get_principal_title(group, _):
            return group.getGroupTitleOrName()
            
        return self._principal_search_results(search_for_principal,
            get_principal_by_id, get_principal_title, 'group', 'groupid')