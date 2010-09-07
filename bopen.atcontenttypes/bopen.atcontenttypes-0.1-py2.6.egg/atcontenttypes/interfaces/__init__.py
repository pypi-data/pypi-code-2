# -*- extra stuff goes here -*-
from zope.interface import Interface
from Products.Archetypes import utils
from richfolder import IRichFolder
import longdescription

class IHaveLongDescription(Interface):
    """Marker interface for content with long_description field"""

# generate zope2 interfaces
_m=utils.makeZ3Bridges
_m(longdescription, IHaveLongDescription)
