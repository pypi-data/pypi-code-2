import zope.schema
from z3c.zalchemy.interfaces import ISQLAlchemyObjectContained, ISQLAlchemyContainer
from zope.app.container.constraints import contains, containers
from zope.interface import Interface, Attribute

from z3c.zalchemy.i18n import _

# Interface defining the Zope schema of message objects
class IHelloWorldMessage3(ISQLAlchemyObjectContained):
    """Information about a hello world message"""

    id = Attribute("The ID of the Message")
    
    who = zope.schema.TextLine(
        title=_(u'Who'),
        description=_(u'Name of the person getting the message'),
        required=True)

#interface defining the schema of the container for message objects
class IMessageContainer3(ISQLAlchemyContainer):
    """A container for hello world message mbjects"""
    contains(IHelloWorldMessage3)
    
