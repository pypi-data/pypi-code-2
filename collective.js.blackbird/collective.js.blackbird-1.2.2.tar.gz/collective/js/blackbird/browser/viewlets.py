from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common

class ToggleBlackbird(common.ViewletBase):
    render = ViewPageTemplateFile('toggle.pt')
