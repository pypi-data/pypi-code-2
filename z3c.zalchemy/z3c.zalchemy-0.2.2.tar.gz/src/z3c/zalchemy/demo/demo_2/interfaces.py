import zope.schema
from z3c.zalchemy.interfaces import ISQLAlchemyObjectContained, ISQLAlchemyContainer
from zope.app.container.constraints import contains, containers

from z3c.zalchemy.i18n import _

# Interface defining the Zope schema for RDBMS-persistent Messages
class IHelloWorldMessage2(ISQLAlchemyObjectContained):
    """Information about a hello world message"""

    who = zope.schema.TextLine(
        title=_(u'Who'),
        description=_(u'Name of the person sending the message'),
        required=True)

# Interface of a container for RDBMS-persistent messages
class IMessageContainer2(ISQLAlchemyContainer):
    """A container for hello world message mbjects"""
    contains(IHelloWorldMessage2)
    
