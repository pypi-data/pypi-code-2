from zope.interface import implements
from zope.component import getUtility

from plone.app.portlets import manager
from plone.app.portlets.browser import editmanager
from plone.app.portlets.browser import manage
from plone.app.portlets.browser.interfaces import IManageColumnPortletsView
from plone.portlets.interfaces import IPortletManager

from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Collage.interfaces import ICollageEditLayer
from Products.Collage.browser.views import BaseView

class ViewRenderer(manager.ColumnPortletManagerRenderer):

    __allow_access_to_unprotected_subobjects__ = 1

    @property
    def error_log(self):
        return getToolByName(self.context,'error_log')

    def inherited_portlets(self):
        return ()

    def can_manage_portlets(self):
        return False

class EditRenderer(editmanager.ContextualEditPortletManagerRenderer):
    def inherited_portlets(self):
        return ()

class ColumnPortletView(Explicit, BaseView, manage.ManageContextualPortlets):
    implements(IManageColumnPortletsView)

    title = u"Portlets Bottom"
    normalized_manager_name = "collage.portletmanager"
    renderer = None
    
    def __init__(self, context, request):
        BaseView.__init__(self, context, request)
        self.manager = getUtility(IPortletManager, name=self.normalized_manager_name)

    def update(self):
        renderer_class = ICollageEditLayer.providedBy(self.request) and \
                         EditRenderer or ViewRenderer
        renderer = renderer_class(self.context, self.request, self, self.manager)
        self.renderer = renderer.__of__(self)
        self.renderer.update()

    def __call__(self):
        self.update()
        return super(ColumnPortletView, self).__call__()

    def is_edit_mode(self):
        return ICollageEditLayer.providedBy(self.request)

class ColumnPortletTopView(ColumnPortletView):
    title = u"Portlets Top"
