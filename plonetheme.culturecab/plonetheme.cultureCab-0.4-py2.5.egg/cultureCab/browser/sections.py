from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase



class GlobalSectionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('sections.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions()
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs()

        selectedTabs = self.context.restrictedTraverse('selectedTabs')
        self.selected_tabs = selectedTabs('index_html',
                                          self.context,
                                          self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']
	
