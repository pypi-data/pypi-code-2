from zope import interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class IPublicLayer(IDefaultBrowserLayer):
    """Browser layer for our public Plone site.
    """

class IPublicLayerOK(interface.Interface):
    """Request has been approved for show in the public skin.
    """
