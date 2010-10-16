from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class INavigationCatalogTool(Interface):
    """ Marker interface for INavigationCatalogTool """

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
