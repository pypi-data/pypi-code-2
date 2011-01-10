from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.workflow.browser.kss_sharing import KSSSharingView as base


class KSSSharingView(base):
    """KSS view for sharing page.
    """

    template = ViewPageTemplateFile('sharing.pt')
