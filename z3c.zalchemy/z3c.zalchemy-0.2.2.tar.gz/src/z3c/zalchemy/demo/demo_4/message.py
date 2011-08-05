from datetime import datetime

import sqlalchemy

import z3c.zalchemy
from z3c.zalchemy.container import contained

from zope.app.container.contained import Contained
from zope.interface import implements
from zope.component import adapts
from zope.schema.fieldproperty import FieldProperty
from zope.component.factory import Factory
from zope.dublincore.interfaces import IZopeDublinCore

from interfaces import IHelloWorldMessage4, IHelloWorldFragment


RelationalDCTable = sqlalchemy.Table(
        'dublin_core',
        z3c.zalchemy.metadata('DemoEngine-4'),
        sqlalchemy.Column('id', sqlalchemy.Integer,
                           sqlalchemy.Sequence('metadata_seq'),
                           primary_key = True),
        sqlalchemy.Column('title', sqlalchemy.Unicode),
        sqlalchemy.Column('description', sqlalchemy.Unicode),
        sqlalchemy.Column('created', sqlalchemy.DateTime),
        sqlalchemy.Column('modified', sqlalchemy.DateTime)
        )
        
z3c.zalchemy.createTable('dublin_core', 'DemoEngine-4')


HelloWorldMessageTable4 = sqlalchemy.Table(
        'message',
        z3c.zalchemy.metadata('DemoEngine-4'),
        sqlalchemy.Column('id', sqlalchemy.Integer,
                           sqlalchemy.ForeignKey(RelationalDCTable.c.id),
                           primary_key = True,
                           autoincrement = False),
        sqlalchemy.Column('who', sqlalchemy.Unicode),
        )

z3c.zalchemy.createTable('message', 'DemoEngine-4')


HelloWorldFragmentTable = sqlalchemy.Table(
        'fragment',
        z3c.zalchemy.metadata('DemoEngine-4'),
        sqlalchemy.Column('id', sqlalchemy.Integer,
                           primary_key = True),
        sqlalchemy.Column('message_id', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey(HelloWorldMessageTable4.c.id)),
        sqlalchemy.Column('what', sqlalchemy.Unicode),
        )

z3c.zalchemy.createTable('fragment', 'DemoEngine-4')


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

            
relationalmapper = sqlalchemy.mapper(RelationalDC, RelationalDCTable)

class RelationalDCAdapter(object):
    adapts(IHelloWorldMessage4)
    implements(IZopeDublinCore)
    
    def __init__(self, context):
        self.context = context
        self.__parent__ = context
        session = z3c.zalchemy.getSession()
        query = session.query(RelationalDC).select_by(id=context.id)
        self.result = None
        try:
            self.result = query[0]
        except IndexError:
            pass
        
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
                           


class HelloWorldFragment(Contained):
    implements(IHelloWorldFragment)                           

    what = FieldProperty(IHelloWorldFragment['what'])

    def __init__(self, what):
        self.what = what

fragmentmapper = sqlalchemy.mapper(HelloWorldFragment, HelloWorldFragmentTable)


class HelloWorldMessage4(Contained):
    implements(IHelloWorldMessage4)

    who = FieldProperty(IHelloWorldMessage4['who'])

    def __init__(self, title, description, who):
        self.rdc = RelationalDC(title, description)
        self.who = who
        


    def keys(self):
        for name, obj in self.items():
            yield name

    def values(self):
        for name, obj in self.items():
            yield obj

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        for obj in self.fragments:
            name = self._toStringIdentifier(obj)
            yield (name, contained(obj, self, name) )

    def __getitem__(self, name):
        if not isinstance(name, basestring):
            raise KeyError, "%s is not a string" % name
        obj = self._fromStringIdentifier(name)
        if obj is None:
            raise KeyError(name)
        return contained(obj, self, name)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default
    
    def __contains__(self, name):
        return self.get(name) is not None

    def __len__(self):
        return len(self.fragments)
        
    def __delitem__(self, name):
        obj = self[name]
        #TODO: better delete objects using a delete adapter
        #      for dependency handling.
        session = z3c.zalchemy.getSession()
        session.delete(obj)

    def __setitem__(self, name, item):
        session = z3c.zalchemy.getSession()
        self.fragments.append(item)
        session.flush()

    def _toStringIdentifier(self, obj):
        session = z3c.zalchemy.getSession()
        mapper = session.mapper(HelloWorldFragment)
        instance_key = mapper.instance_key(obj)
        ident = '-'.join(map(str, instance_key[1]))
        return 'HelloWorldFragment-'+ident

    def _fromStringIdentifier(self, name):
        prefix = 'HelloWorldFragment' + '-'
        if not name.startswith(prefix):
            return None

        ident = name[len(prefix):]
        session = z3c.zalchemy.getSession()
        return session.query(HelloWorldFragment).get_by(id=ident)


messagemapper = sqlalchemy.mapper(HelloWorldMessage4, HelloWorldMessageTable4)
messagemapper.add_property('rdc', sqlalchemy.relation(RelationalDC,
                                                      cascade="all"))
messagemapper.add_property('fragments',
                           sqlalchemy.relation(HelloWorldFragment,
                                               cascade="all"))

messageFactory=Factory(
    HelloWorldMessage4,
    title=u"Create a new message",
    description=u"This factory instantiates new messages"
    )
    
fragmentFactory=Factory(
    HelloWorldFragment,
    title=u"Create a new message fragment",
    description=u"This factory instantiates new message fragments"
    )
