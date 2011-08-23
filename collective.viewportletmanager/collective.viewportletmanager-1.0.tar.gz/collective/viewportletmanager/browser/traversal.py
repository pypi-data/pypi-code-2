from zope.interface import implements, Interface
from zope.component import adapts, getUtility
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest

from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.storage import PortletAssignmentMapping

from collective.viewportletmanager.config import VIEW_CATEGORY


class ViewPortletNamespace(object):
    """Used to traverse to a view portlet assignable
    """
    implements(ITraversable)
    adapts(Interface, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        col, view_key = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[VIEW_CATEGORY]
        manager = category.get(view_key, None)
        if manager is None:
            manager = category[view_key] = PortletAssignmentMapping(manager=col,
                category=VIEW_CATEGORY, name=view_key)

        # XXX: For graceful migration
        if not getattr(manager, '__manager__', None):
            manager.__manager__ = col
        if not getattr(manager, '__category__', None):
            manager.__category__ = VIEW_CATEGORY
        if not getattr(manager, '__name__', None):
            manager.__name__ = view_key

        return manager
