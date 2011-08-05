import zope.schema
from z3c.zalchemy.interfaces import ISQLAlchemyObjectContained, ISQLAlchemyContainer
from zope.app.container.constraints import contains, containers
from zope.interface import Interface, Attribute

from z3c.zalchemy.i18n import _

# Define a message fragment, which is contained in a message
class IHelloWorldFragment(ISQLAlchemyObjectContained):
    """Information about a hello world message"""
    
    message_id = Attribute("The ID of the parent message")

    what = zope.schema.TextLine(
        title=_(u'What'),
        description=_(u'fragment of a message'),
        required=True)

# Define a message object, which contains fragments, and
# is contained in a MessageContainer        
class IHelloWorldMessage4(ISQLAlchemyContainer,ISQLAlchemyObjectContained):
    """Information about a hello world message"""

    id = Attribute("The ID of the Message")
    
    fragments = Attribute("The contained Message fragments")
    
    who = zope.schema.TextLine(
        title=_(u'Who'),
        description=_(u'Name of the person getting the message'),
        required=True)
    contains(IHelloWorldFragment)

# Define a container for Messages
class IMessageContainer4(ISQLAlchemyContainer):
    """A container for hello world message mbjects"""
    contains(IHelloWorldMessage4)
    
