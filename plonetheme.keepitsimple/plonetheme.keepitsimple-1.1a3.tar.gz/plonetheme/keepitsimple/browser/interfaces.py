#from plonetheme.classic.browser.interfaces import IDefaultPloneLayer
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class IPortalIntro(IViewletManager):
    """A viewlet manager for the intro and 
    """
