from Products.Five import BrowserView
from zope.component import getMultiAdapter
from Products.PlonePAS.browser.search import PASSearchView

class SearchGroups(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def searchGroups(self,searchstring):
        """
        Search in titles and id of groups
        @author: mirco
        """
        if not isinstance(self.context, PASSearchView):
            search_view = getMultiAdapter((self.context, self.request), name='pas_search')
        else:
            search_view = self.context
        groups_by_id = search_view.searchGroups(id=searchstring)
        groups_by_name = search_view.searchGroups(name=searchstring)
        groups_id = {}
        for group in groups_by_id+groups_by_name:
            if group.get('id') not in groups_id.keys():
                groups_id[group.get('id')] = group
        ids = groups_id.keys()
        ids.sort()
        result_groups = []
        for id in ids:
            result_groups.append(groups_id[id])
        return tuple(result_groups)
