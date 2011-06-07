from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, LogoViewlet as LogoViewletBase
from zope.component import getMultiAdapter

class LogoViewlet(LogoViewletBase):
    render = ViewPageTemplateFile('templates/logo.pt')
    def update(self):
        context = aq_inner(self.context)
        portal = getMultiAdapter((context, self.request),
                                 name=u'plone_portal_state')
        helper = getMultiAdapter((context, self.request),
                                 name=u'pythonbrasil_helper')
        ano = helper.ano()
        portal_url = portal.portal_url()
        # Every edition is a root
        self.navigation_root_url = '%s/%s' % (portal_url,ano)
        logoName = 'img_%s/logo.png' % ano
        try:
            logo_tag = context.unrestrictedTraverse(logoName).tag()
        except AttributeError:
            logoName = 'logo.png'
            logo_tag = context.unrestrictedTraverse(logoName).tag()
        self.logo_tag = logo_tag
                

