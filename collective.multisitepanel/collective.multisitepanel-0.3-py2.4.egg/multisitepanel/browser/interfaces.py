from plone.theme.interfaces import IDefaultPloneLayer
from zope import interface

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IMultiSitePanel(interface.Interface):
    pass

class IMultiSiteProductsPanel(interface.Interface):
    pass