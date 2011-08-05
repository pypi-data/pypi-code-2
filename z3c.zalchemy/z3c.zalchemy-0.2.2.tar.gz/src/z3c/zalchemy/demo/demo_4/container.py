from zope.app.container.contained import Contained
from persistent import Persistent
from zope.interface import implements

import z3c.zalchemy
from z3c.zalchemy.container import contained

from interfaces import IMessageContainer4
from message import HelloWorldMessage4


    
class MessageContainer4(Persistent, Contained):
    implements(IMessageContainer4)

    def keys(self):
        for name, obj in self.items():
            yield name

    def values(self):
        for name, obj in self.items():
            yield obj

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        session = z3c.zalchemy.getSession()
        query = session.query(HelloWorldMessage4)
        for obj in query.select():
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
        try:
            session = z3c.zalchemy.getSession()
            query = session.query(HelloWorldMessage4)
            return query.count()
        except sqlalchemy.exceptions.SQLError:
            # we don't want an exception in case of database problems
            return 0

    def __delitem__(self, name):
        obj = self[name]
        #TODO: better delete objects using a delete adapter
        #      for dependency handling.
        session = z3c.zalchemy.getSession()
        session.delete(obj)

    def __setitem__(self, name, item):
        session = z3c.zalchemy.getSession()
        session.save(item)
        session.flush()

    def _toStringIdentifier(self, obj):
        session = z3c.zalchemy.getSession()
        mapper = session.mapper(HelloWorldMessage4)
        instance_key = mapper.instance_key(obj)
        ident = '-'.join(map(str, instance_key[1]))
        return 'HelloWorldMessage4-'+ident

    def _fromStringIdentifier(self, name):
        prefix = 'HelloWorldMessage4-'
        if not name.startswith(prefix):
            return None

        ident = name[len(prefix):]
        session = z3c.zalchemy.getSession()
        return session.query(HelloWorldMessage4).get(ident)

