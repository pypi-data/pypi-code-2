from zope.interface import Interface

class IPortletsAwareView(Interface):
    """Marker interface for zope 3 view that wants to have portlets
    assigned to it.
    """
