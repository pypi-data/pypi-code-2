from plone.app.layout.viewlets.common import SearchBoxViewlet as CustomSearchBoxViewlet
from plone.app.layout.viewlets.common import SkipLinksViewlet as _SkipLinksViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SearchBoxViewlet(CustomSearchBoxViewlet):
    render = ViewPageTemplateFile('searchbox.pt')


class SkipLinksViewlet(_SkipLinksViewlet):
    index = ViewPageTemplateFile('skip_links.pt')
