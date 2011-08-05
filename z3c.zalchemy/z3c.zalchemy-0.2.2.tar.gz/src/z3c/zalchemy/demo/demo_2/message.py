import sqlalchemy
import z3c.zalchemy

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from interfaces import IHelloWorldMessage2

from zope.component.factory import Factory

# define and create the RDBMS table for storing messages
HelloWorldMessageTable2 = sqlalchemy.Table(
        'message', 
        z3c.zalchemy.metadata('DemoEngine-2'),
        sqlalchemy.Column('id', sqlalchemy.Integer,
                           primary_key = True),
        sqlalchemy.Column('who', sqlalchemy.Unicode),
        )

z3c.zalchemy.createTable('message', 'DemoEngine-2')

#Define the python class for messages
class HelloWorldMessage2(object):
    implements(IHelloWorldMessage2)

    who = FieldProperty(IHelloWorldMessage2['who'])

    def __init__(self, who):
        self.who = who

# Map the message class to the message table
messagemapper = sqlalchemy.mapper(HelloWorldMessage2, HelloWorldMessageTable2)

messageFactory=Factory(
    HelloWorldMessage2,
    title=u"Create a new message",
    description=u"This factory instantiates new messages"
    )
