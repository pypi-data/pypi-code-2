from zope.component import getMultiAdapter

from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from zope.component import queryUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from atreal.layouts.browser.controlpanel import IatRealLayoutsSchema

class DocumentActionsViewlet(ViewletBase):
    def update(self):
        super(DocumentActionsViewlet, self).update()

        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.actions = self.context_state.actions().get('document_actions', None)

    index = ViewPageTemplateFile("document_actions.pt")


class restrictedAccessViewlet(ViewletBase):
    """
    """
    
    @property
    def _options(self):
        """
        """
        _siteroot = queryUtility(IPloneSiteRoot)
        return IatRealLayoutsSchema(_siteroot)
    
    @property
    def anonurls(self):
        """
        """
        anonurls = getattr(self._options, 'atreallayouts_restricted_access_anonurls', '')
        if anonurls is None or anonurls == '':
            return []
        return anonurls.split('\n')

    def render(self):
        """
        """
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        if not self.portal_state.anonymous():
            return u""
        url = self.request.get("URL")
        for okurl in self.anonurls:
            if okurl in url:
                return u""
        login = self.portal_state.portal_url() + "/login_form"
        if url == login:
            return u""
        self.request.response.redirect(login)
        return u""
    