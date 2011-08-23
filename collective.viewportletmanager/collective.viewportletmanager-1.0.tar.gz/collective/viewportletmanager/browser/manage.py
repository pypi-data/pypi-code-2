from Acquisition import aq_inner

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from Products.Archetypes.utils import shasattr

from plone.portlets.constants import GROUP_CATEGORY, CONTENT_TYPE_CATEGORY, \
    CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager, \
    ILocalPortletAssignmentManager, IPortletAssignmentMapping
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.browser.manage import ManagePortletsViewlet, \
    ManageContextualPortlets as base
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.layout.viewlets.common import ViewletBase

from collective.viewportletmanager.config import VIEW_CATEGORY
from collective.viewportletmanager.browser.interfaces import \
    IManageViewPortletsView


class ManageContextualPortlets(base):
    """Override it in order to provide custom set_blacklist_status action
    to also manipulate View Portlets related settings.
    """
    
    # view @@set-portlet-blacklist-status
    def set_blacklist_status(self, manager, group_status, content_type_status,
                             context_status, view_status):
        portletManager = getUtility(IPortletManager, name=manager)
        assignable = getMultiAdapter((self.context, portletManager,),
            ILocalPortletAssignmentManager)
        assignments = getMultiAdapter((self.context, portletManager),
            IPortletAssignmentMapping)

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        def int2status(status):
            if status == 0:
                return None
            elif status > 0:
                return True
            else:
                return False

        assignable.setBlacklistStatus(GROUP_CATEGORY, int2status(group_status))
        assignable.setBlacklistStatus(CONTENT_TYPE_CATEGORY,
            int2status(content_type_status))
        assignable.setBlacklistStatus(CONTEXT_CATEGORY,
            int2status(context_status))
        # actual patch, set VIEW_CATEGORY black list
        assignable.setBlacklistStatus(VIEW_CATEGORY,
            int2status(view_status))

        baseUrl = str(getMultiAdapter((self.context, self.request),
            name='absolute_url'))
        self.request.response.redirect(baseUrl + '/@@manage-portlets')
        return ''

class ManageViewPortlets(BrowserView):
    """manage-view-portelts view to edit View based Portlets"""
    
    implements(IManageViewPortletsView)

    def __init__(self, context, request):
        super(ManageViewPortlets, self).__init__(context, request)
        self.request.set('disable_border', True)

    # IManagePortletsView implementation

    @property
    def macros(self):
        return self.index.macros

    @property
    def category(self):
        return VIEW_CATEGORY

    @property
    def key(self):
        return self.request['key']

    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request),
            name='absolute_url'))
        view_key = self.request['key']
        return '%s/++viewportlets++%s+%s' % (baseUrl, manager.__name__,
            view_key)

    def getAssignmentsForManager(self, manager):
        view_key = self.request['key']
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[VIEW_CATEGORY]
        mapping = category.get(view_key, None)
        if mapping is None:
            mapping = category[view_key] = PortletAssignmentMapping(
                manager=manager.__name__, category=VIEW_CATEGORY, name=view_key)
        return mapping.values()

    # View attributes

    @property
    def view_name(self):
        """Key is in format: "uid:view_name"""
        return self.request['key'].split(':')[1]

class ManageViewPortletsViewlet(ManagePortletsViewlet):
    """A viewlet base class for viewlets that need to render on the
    manage view portlets screen.
    """
    implements(IManageViewPortletsView)

class ManageViewPortletsLinkViewlet(ViewletBase):
    """Displays link to manage view portlets"""
    
    template = ViewPageTemplateFile('templates/manage-view-link.pt')
    
    def update(self):
        self.available = True
        
        # prepare url to manage view portlets
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
            name='plone_context_state')
        obj = context_state.canonical_object()
        
        # this is a key we're using to assign view portlets: uid:view_name
        uid = 'nouid'
        if shasattr(obj, 'UID'):
            uid = obj.UID()
        key = '%s:%s' % (uid, str(self.view.__name__))
        self.url = '%s/@@manage-view-portlets?key=%s' % (obj.absolute_url(),
            key)
    
    def render(self):
        return self.template()
