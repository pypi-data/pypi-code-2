from datetime import datetime

import sqlalchemy

import z3c.zalchemy

from zope.interface import implements
from zope.component import adapts
from zope.schema.fieldproperty import FieldProperty
from zope.component.factory import Factory
from zope.dublincore.interfaces import IZopeDublinCore

from interfaces import IHelloWorldMessage3

# Define and create the table for storing dublin core metadata
RelationalDCTable = sqlalchemy.Table(
        'dublin_core',
        z3c.zalchemy.metadata('DemoEngine-3'),
        sqlalchemy.Column('id', sqlalchemy.Integer,
                           sqlalchemy.Sequence('metadata_seq'),
                           primary_key = True),
        sqlalchemy.Column('title', sqlalchemy.Unicode),
        sqlalchemy.Column('description', sqlalchemy.Unicode),
        sqlalchemy.Column('created', sqlalchemy.DateTime),
        sqlalchemy.Column('modified', sqlalchemy.DateTime)
        )
        
z3c.zalchemy.createTable('dublin_core', 'DemoEngine-3')

# Define and create the table for storing the message
# Note the explicit setting of the FK relationship, and that the
# primary key does *not* autoincrement
HelloWorldMessageTable3 = sqlalchemy.Table(
        'message',
        z3c.zalchemy.metadata('DemoEngine-3'),
        sqlalchemy.Column('id', sqlalchemy.Integer,
                           sqlalchemy.ForeignKey(RelationalDCTable.c.id),
                           primary_key = True,
                           autoincrement = False),
        sqlalchemy.Column('who', sqlalchemy.Unicode),
        )

z3c.zalchemy.createTable('message', 'DemoEngine-3')

# The class defining the object containing the metadata
class RelationalDC(object):
    
    creators = FieldProperty(IZopeDublinCore['creators'])
    title = FieldProperty(IZopeDublinCore['title'])
    description = FieldProperty(IZopeDublinCore['description'])
    created = FieldProperty(IZopeDublinCore['created'])
    modified = FieldProperty(IZopeDublinCore['modified'])
    
    
    def __init__(self, title=None, description=None, created=None,
                 modified=None):
        self.title = title
        self.description = description
        if created is None:
            self.created = datetime.now()
        else:
            self.created = created
        if modified is None:
            self.modified = datetime.now()
        else:
            self.modified = modified

# Map the metadata table to the metadata class
relationalmapper = sqlalchemy.mapper(RelationalDC, RelationalDCTable)

# The class defining the adapter between the message object and the
# IZopeDublinCore interface.
class RelationalDCAdapter(object):
    adapts(IHelloWorldMessage3)
    implements(IZopeDublinCore)
    
    # The adapter implementation selects the correct
    # RelationalDC instance based on the message id.
    def __init__(self, context):
        self.context = context
        self.__parent__ = context
        session = z3c.zalchemy.getSession()
        query =  session.query(RelationalDC).select_by(id=context.id)
        self.result = None
        try:
            self.result = query[0]
        except IndexError:
            pass
    
    # faking the creators property for now
    def getCreators(self):
        return ()
    
    def setCreators(self, creators):
        pass
        
    creators = property(getCreators, setCreators, doc="RelationalDC creators")
        
    def getTitle(self):
        return self.result.title
    
    def setTitle(self, title):
        self.result.title = title
        
    title = property(getTitle, setTitle, doc="RelationalDC title")
            
    def getDescription(self):
        return self.result.description
    
    def setDescription(self, description):
        self.result.description = description
        
    description = property(getDescription, setDescription,
                           doc="RelationalDC description")
                           
                           
# The class defining the message object
class HelloWorldMessage3(object):
    implements(IHelloWorldMessage3)

    who = FieldProperty(IHelloWorldMessage3['who'])
    
    # instantiate a RelationalDC object to get an id
    # (the metadata.id column autoincrements)
    def __init__(self, title, description, who):
        self.rdc = RelationalDC(title, description)
        self.who = who
        

# map the message class to the message table
messagemapper = sqlalchemy.mapper(HelloWorldMessage3, HelloWorldMessageTable3)
# add an additional property to the message mapper that maps
# to the metadata class
messagemapper.add_property('rdc', sqlalchemy.relation(RelationalDC,
                                                      cascade="all"))

messageFactory=Factory(
    HelloWorldMessage3,
    title=u"Create a new message",
    description=u"This factory instantiates new messages"
    )
