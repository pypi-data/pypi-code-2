import sqlalchemy
import z3c.zalchemy
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from interfaces import IHelloWorldMessage

from zope.component.factory import Factory

# Define and create the table object for storing messages
HelloWorldMessageTable = sqlalchemy.Table(
        'message',
        z3c.zalchemy.metadata('DemoEngine-1'),
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True),
        sqlalchemy.Column('who', sqlalchemy.Unicode),
        )

z3c.zalchemy.createTable('message', 'DemoEngine-1')

# Define the content class for messages
class HelloWorldMessage(object):
    implements(IHelloWorldMessage)

    who = FieldProperty(IHelloWorldMessage['who'])

    def __init__(self, who):
        self.who = who

    def __repr__(self):
        return '<%s from %r>' %(self.__class__.__name__, self.who)


# Map the table to the class
sqlalchemy.mapper(HelloWorldMessage, HelloWorldMessageTable)

messageFactory=Factory(
    HelloWorldMessage,
    title=u"Create a new message",
    description=u"This factory instantiates new messages"
    )
