from zope.interface import Interface, Attribute
from zope.component.interfaces import IObjectEvent

class ICropModifiedEvent(IObjectEvent):
    """A cropping has been modified"""
    fieldname = Attribute("The field name")
    imageid = Attribute("The id of the crop")
    object = Attribute("The context")
    image = Attribute("The image itself")


class IRichImage(Interface):
    """Image with crop functionalities"""
