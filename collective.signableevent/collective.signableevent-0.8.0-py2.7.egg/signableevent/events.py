from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
from collective.signableevent.interfaces import ISignupAddedEvent

class SignupAddedEvent(ObjectModifiedEvent):
    """ """
    implements(ISignupAddedEvent)


            
