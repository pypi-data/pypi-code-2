from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets import common

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName



class SearchBoxViewlet(common.SearchBoxViewlet, ViewletBase):
    render = ViewPageTemplateFile('templates/searchbox.pt')
    
    def update(self):
        super(SearchBoxViewlet, self).update()
        self.site_url = self.portal_url

class IntroTextViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/intro_text.pt')

    def update(self):
        pass

