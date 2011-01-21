from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IGallerifficView(Interface):
    """ Marker interface"""

class IGallerifficSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """