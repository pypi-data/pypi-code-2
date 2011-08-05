##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from persistent import Persistent

from zope.security.proxy import removeSecurityProxy
from zope.proxy import ProxyBase, sameProxiedObjects

from zope.app.container.contained import Contained
from zope.app.container.contained import ContainedProxy
from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import IContained
from zope.location.interfaces import ILocation
from zope.exceptions.interfaces import UserError

from zope import interface
from zope.interface import directlyProvides, directlyProvidedBy
from zope.configuration.name import resolve

import sqlalchemy
import z3c.zalchemy

from interfaces import ISQLAlchemyContainer


def contained(obj, parent=None, name=None):
    """An implementation of zope.app.container.contained.contained
    that doesn't generate events, for internal use.

    Borrowed from SQLOS.
    """
    if (parent is None):
        raise TypeError, 'Must provide a parent'

    if not IContained.providedBy(obj):
        if ILocation.providedBy(obj):
            directlyProvides(obj, IContained, directlyProvidedBy(obj))
        else:
            obj = ContainedProxy(obj)

    oldparent = obj.__parent__
    oldname = obj.__name__

    if (oldparent is None) or not (oldparent is parent
                                   or sameProxiedObjects(oldparent, parent)):
        obj.__parent__ = parent

    if oldname != name and name is not None:
        obj.__name__ = name

    return obj


class SQLAlchemyNameChooser(NameChooser):

    def checkName(self, name, content):
        if isinstance(name, str):
            name = unicode(name)
        elif not isinstance(name, unicode):
            raise TypeError("Invalid name type", type(name))

        unproxied = removeSecurityProxy(self.context)
        if not name.startswith(unproxied._class.__name__+'-'):
            raise UserError("Invalid name for SQLAlchemy object")
        return True

    def chooseName(self, name, obj):
        # flush the object to make sure it contains an id
        session = z3c.zalchemy.getSession()
        session.save(obj)
        session.flush()
        return self.context._toStringIdentifier(obj)


class SQLAlchemyContainer(Persistent, Contained):
    interface.implements(ISQLAlchemyContainer)

    _className = ''
    _class = None

    def setClassName(self, name):
        self._className = name
        self._class=resolve(name)

    def getClassName(self):
        return self._className
    className = property(getClassName, setClassName)

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
        query = session.query(self._class)
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
            query = session.query(self._class)
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
        mapper = session.mapper(obj.__class__)
        instance_key = mapper.instance_key(obj)
        ident = '-'.join(map(str, instance_key[1]))
        return '%s-%s'%(instance_key[0].__name__, ident)

    def _fromStringIdentifier(self, name):
        class_base_name = self._class.__name__
        prefix = class_base_name + '-'
        if not name.startswith(prefix):
            return None

        ident = name[len(prefix):]
        keys = ident.split('-')
        session = z3c.zalchemy.getSession()
        return session.query(self._class).get([str(key) for key in keys])

