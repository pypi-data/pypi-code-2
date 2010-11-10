from Acquisition import aq_inner, aq_parent

from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from raptus.backlink import RaptusBacklinkMessageFactory as _

class Viewlet(ViewletBase):
    """ Viewlet displaying a backlink
    """
    index = ViewPageTemplateFile('back.pt')

    @property
    @memoize
    def parent(self):
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        parent = aq_parent(aq_inner(self.context))
        if context_state.is_default_page():
            parent = aq_parent(parent)
        if not IContentish.providedBy(parent) and not IPloneSiteRoot.providedBy(parent):
            return
        return {'url': parent.absolute_url(),
                'title': _(u'back to ${parent}', mapping=dict(parent=safe_unicode(parent.Title())))}
