from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class subskinsloader(ViewletBase):
    render = ViewPageTemplateFile('subskinsloader.pt')
