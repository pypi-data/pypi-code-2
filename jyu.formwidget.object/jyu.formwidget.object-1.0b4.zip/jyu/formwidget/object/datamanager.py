# -*- coding: utf-8 -*-
"""DataManager for ObjectField"""

from Acquisition import aq_base

from five import grok

from zope.event import notify
from zope.lifecycleevent import\
    ObjectCreatedEvent, ObjectModifiedEvent, Attributes

from zope.interface import Interface, alsoProvides

from zope.component import queryMultiAdapter, getMultiAdapter

from zope.schema import getFieldNames
from zope.schema.interfaces import IObject

from zope.location.interfaces import IContained
from zope.location.location import locate

from z3c.form.interfaces import\
    IDataManager, IObjectFactory, NO_VALUE

from jyu.formwidget.object.converter import TransientObject


class ObjectField(grok.MultiAdapter):
    grok.provides(IDataManager)
    grok.adapts(Interface, IObject)

    def __init__(self, data, field):
        self.data = data
        self.field = field

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        if not hasattr(self.data, self.field.__name__):
            raise AttributeError
        return getattr(self.data, self.field.__name__)

    def query(self, default=NO_VALUE):
        """See z3c.form.interfaces.IDataManager"""
        return getattr(self.data, self.field.__name__, default)

    def createObject(self, value):
        """Create object using factory adapted for field's schema"""
        # keep value passed, maybe some subclasses want it
        # value here is the raw extracted from the widget's subform
        # in the form of a dict key:fieldname, value:fieldvalue
        name = "%s.%s" % (self.field.schema.__module__,
                          self.field.schema.__name__)
        # IObjectFactory was designed to be called within IDataConverter,
        # but here only context=self.data is known. Therefore we can query
        # it only with context and then tree Interface-base classes.
        creator = queryMultiAdapter(
            (self.data, Interface, Interface, Interface),
            IObjectFactory, name=name)
        if not creator:
            raise ValueError(\
                "No IObjectFactory adapter registered for %s" % name)
        data = dict()
        for name in getFieldNames(self.field.schema):
            data[name] = getattr(value, name, NO_VALUE)
        return creator(data)

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""

        if self.field.readonly:
            raise TypeError("Can't set values on read-only field name=%s"
                            % self.field.__name__)

        if not hasattr(aq_base(self.data), self.field.__name__)\
                or not getattr(aq_base(self.data), self.field.__name__):
            obj = self.createObject(value)
            if not self.field.schema.providedBy(obj):
                alsoProvides(obj, self.field.schema)

            obj.id = self.field.__name__
            setattr(self.data, self.field.__name__, obj)

            locate(obj, self.data, self.field.__name__)
            if not IContained.providedBy(obj):
                alsoProvides(obj, IContained)
            notify(ObjectCreatedEvent(obj))

        names = []
        for name in getFieldNames(self.field.schema):
            dm = getMultiAdapter((
                    getattr(self.data, self.field.__name__),
                    self.field.schema.get(name)
                    ), IDataManager)
            sub_value = getattr(value, name, NO_VALUE)
            if isinstance(sub_value, TransientObject):
                dm.set(sub_value)
            elif sub_value != dm.query(NO_VALUE):
                dm.set(sub_value)
                names.append(name)

        notify(ObjectModifiedEvent(
                getattr(self.data, self.field.__name__),
                Attributes(self.field.schema, *names)))

    def canAccess(self):
        """See z3c.form.interfaces.IDataManager"""
        return True

    def canWrite(self):
        """See z3c.form.interfaces.IDataManager"""
        return True
