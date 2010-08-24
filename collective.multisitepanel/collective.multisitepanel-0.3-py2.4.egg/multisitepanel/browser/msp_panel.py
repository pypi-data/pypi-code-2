import OFS.Folder
from zope import interface
from collective.multisitepanel.browser.interfaces import IMultiSitePanel
from Products.Five import BrowserView
from Products.Five.browser import pagetemplatefile
from collective.multisitepanel import MultisitePanelMessageFactory as _

class MultiSitePanel(OFS.Folder.Folder):
    interface.implements(IMultiSitePanel)

    def Title(self):
        return u"Multisite Panel"
    
class ControlPanelView(BrowserView):
    __call__ = pagetemplatefile.ViewPageTemplateFile('templates/msp_panel.pt')

    label = _(u"Multisite panel")

    def back_link(self):
        return dict(label=_(u"Up to Site Setup"),
                    url=self.context.absolute_url() + '/plone_control_panel')