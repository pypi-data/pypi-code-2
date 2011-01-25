from plone.app.portlets.browser.manage import ManageContextualPortletsViewlet as base
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from quintagroup.theme.schools.browser.interfaces import IThemeSchoolsPortlets


class TopPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the content-well portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IThemeSchoolsPortlets)
    template = ViewPageTemplateFile('templates/renderer.pt')


class ManageContextualPortletsViewlet(base):
    """Viewlet for @@manage-portlets view to make portlets inserted via this
    viewlet editable.

    And this viewlet fix problem with kss edit. It just add __name__ attribute
    which is required for ajax functionality.
    """

    def __init__(self, context, request, view, manager):
        super(ManageContextualPortletsViewlet, self).__init__(context, request, view, manager)
        self.__name__ = view.__name__


class TopPortletsViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/top_portlets.pt')
        
    def update(self):
        """
        Define everything we want to call in the template
        """
        context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        self.manageUrl =  '%s/@@manage-topportlets' % context_state.view_url()
        
        ## This is the way it's done in plone.app.portlets.manager, so we'll do the same
        mt = getToolByName(self.context, 'portal_membership')
        self.canManagePortlets = mt.checkPermission('Portlets: Manage portlets', self.context)
