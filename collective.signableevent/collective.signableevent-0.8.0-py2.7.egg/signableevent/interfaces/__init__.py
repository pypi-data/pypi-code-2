# -*- extra stuff goes here -*-
from eventsignup import IEventSignup
from signableevent import ISignableEvent

from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

class ISignupAddedEvent(IObjectModifiedEvent):
    """ event marker """
    
class ISignableEventTool(Interface):
    """ marker interface """
