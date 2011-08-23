from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.portlets.browser.interfaces import IManageColumnPortletsView

class IViewPortletManagerLayer(IDefaultPloneLayer):
    """A layer specific to collective.viewportletmanager product.
    """

class IManageViewPortletsView(IManageColumnPortletsView):
    """Marker for the manage view portlets view
    """
