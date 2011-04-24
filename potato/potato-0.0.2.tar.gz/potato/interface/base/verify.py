
from zope.interface import Interface, Attribute

class IVerifiable(Interface):
    """
    An object which provides an interface. 
    """
    __interface__ = Attribute("The interface which the object defines.")
    __name__ = Attribute("The name of the object.")
    __version__ = Attribute("The version of the object.")
