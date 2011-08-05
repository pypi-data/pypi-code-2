import zope.schema
from z3c.zalchemy.interfaces import ISQLAlchemyObjectContained, ISQLAlchemyContainer
from zope.app.container.constraints import contains, containers

from z3c.zalchemy.i18n import _

# Define an interface for an RDBMS-persistent content class

class IHelloWorldMessage(ISQLAlchemyObjectContained):
    """Information about a hello world message"""

    who = zope.schema.TextLine(
        title=_(u'Who'),
        description=_(u'Name of the person sending the message'),
        required=True)

# Define an interface for a container of RDBMS-persistent IHelloWorld objects

class IMessageContainer(ISQLAlchemyContainer):
    """A container for hello world message mbjects"""
    contains(IHelloWorldMessage)
    
