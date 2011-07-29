from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from plone.app.portlets.portlets.events import Renderer
from DateTime.DateTime import DateTime

#
# Monkey-patch's Plone events portlet so we display SignableEvents too
#

def _data(self):
    context = aq_inner(self.context)
    catalog = getToolByName(context, 'portal_catalog')
    limit = self.data.count
    state = self.data.state
    path = self.navigation_root_path
    return catalog(portal_type=('Event','SignableEvent',),
                   review_state=state,
                   end={'query': DateTime(),
                        'range': 'min'},
                   path=path,
                   sort_on='start',
                   sort_limit=limit)[:limit]
Renderer._data = _data
