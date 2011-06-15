from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IContactFolder(Interface):
    """ A contacts folder content type """

class IContact(Interface):
    """ A contact content type """

class ISiteContactsLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """
