from z3c.zalchemy.container import SQLAlchemyContainer
from interfaces import IMessageContainer
from message import HelloWorldMessage
from zope.interface import implements

# Subclass The SQLAlchemyContainer class to set an explicit class name to use

class MessageContainer(SQLAlchemyContainer):
    """A container for Hello World messages"""
    implements(IMessageContainer)
    def __init__(self):
        super(MessageContainer, self).__init__(self)
        self.setClassName('z3c.zalchemy.demo.demo_1.message.HelloWorldMessage')

