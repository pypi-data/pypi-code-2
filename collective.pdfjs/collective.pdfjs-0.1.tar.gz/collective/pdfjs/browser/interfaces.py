from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer

class IInlinePDFSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
    
class IInlinePDFView(Interface):
    """
    Inline PDF View interface
    """