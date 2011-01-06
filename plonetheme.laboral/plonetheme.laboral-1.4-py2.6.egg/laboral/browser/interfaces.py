from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from zope.interface import implements, Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IHeadManager(IViewletManager):
    """Viewlet manager on top of the site to contain the logo and searchbox
    """

class IFooterManager(IViewletManager):
    """Viewlet manager on bottom of the site to contain the login menu
    """
    
class ISlider(Interface):
    """Viewlet manager on bottom of the site to contain the login menu
    """