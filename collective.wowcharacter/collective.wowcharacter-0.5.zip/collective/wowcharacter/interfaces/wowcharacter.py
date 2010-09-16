from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.wowcharacter import wowcharacterMessageFactory as _

class IWoWCharacter(Interface):
    """An installable content type for WoW characters"""
    
    # -*- schema definition goes here -*-
