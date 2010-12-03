from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IHeadManager(IViewletManager):
    """Viewlet manager on top of the site to contain the logo and searchbox
    """
