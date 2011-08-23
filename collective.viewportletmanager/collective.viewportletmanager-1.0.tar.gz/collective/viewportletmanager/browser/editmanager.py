from zope.interface import Interface
from zope.component import adapts, getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.editmanager import \
    ContextualEditPortletManagerRenderer as base, EditPortletManagerRenderer

from collective.viewportletmanager.browser.interfaces import \
    IViewPortletManagerLayer, IManageViewPortletsView
from collective.viewportletmanager.config import VIEW_CATEGORY


class ContextualEditPortletManagerRenderer(base):
    """Render a portlet manager in edit mode for contextual portlets.
    
    We override it here in order to add 'View portlets' dropdown setting to
    @@manage-portlets view.
    """
    adapts(Interface, IViewPortletManagerLayer, IManageContextualPortletsView,
        IPortletManager)

    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')

    def view_blacklist_status(self):
        assignable = getMultiAdapter((self.context, self.manager),
            ILocalPortletAssignmentManager)
        return assignable.getBlacklistStatus(VIEW_CATEGORY)

class ViewEditPortletManagerRenderer(EditPortletManagerRenderer):
    """Render a portlet manager in edit mode for manage view portlets page.
    
    We override it to get rid of inherited portlets on manage view portlets
    page.
    """
    adapts(Interface, IViewPortletManagerLayer, IManageViewPortletsView,
        IPortletManager)

    def inherited_portlets(self):
        return ()
