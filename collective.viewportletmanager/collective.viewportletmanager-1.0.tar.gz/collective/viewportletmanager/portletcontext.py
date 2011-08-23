from Acquisition import aq_inner

from zope.interface import implements

from Products.Archetypes.utils import shasattr

from plone.portlets.interfaces import IPortletContext
from plone.app.portlets import portletcontext as base

from collective.viewportletmanager.config import VIEW_CATEGORY


class ContentContext(base.ContentContext):
    """We override it here in order to retrieve view portlets.
    """
    implements(IPortletContext)

    def globalPortletCategories(self, placeless=False, view=None):
        cats = super(ContentContext, self).globalPortletCategories(placeless)
        view_key = self._getViewKey(view)
        if view_key is not None:
            cats.append((VIEW_CATEGORY, view_key,))
        return cats

    def _getViewKey(self, view):
        """Trying to figure out view key"""
        if view is None:
            return None

        # this is a key we're using to assign view portlets: uid:view_name
        context = aq_inner(self.context)
        uid = 'nouid'
        if shasattr(context, 'UID'):
            uid = context.UID()

        return '%s:%s' % (uid, str(view.__name__))
