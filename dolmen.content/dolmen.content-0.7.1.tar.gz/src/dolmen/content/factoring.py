# -*- coding: utf-8 -*-

from dolmen.content import name, title, description, get_schema
from dolmen.content.interfaces import IFactory
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements, implementedBy


def default_name(component, module=None, **data):
    return component.__name__


class Factory(object):
    """A content type generic factory.
    """
    implements(IFactory)

    addform = FieldProperty(IFactory['addform'])

    def __init__(self, factory):
        self.factory = factory

    def getInterfaces(self):
        return implementedBy(self.factory)

    def getSchema(self):
        return get_schema(self.factory)

    @property
    def name(self):
        return name.bind(get_default=default_name).get(self.factory)

    @property
    def title(self):
        return title.bind(default=u"").get(self.factory)

    @property
    def description(self):
        return description.bind(default=u"").get(self.factory)

    def __call__(self, *args, **kw):
        return self.factory(*args, **kw)
