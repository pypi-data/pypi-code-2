# -*- coding: utf-8 -*-

import grokcore.content
from dolmen.content import interfaces, require
from dolmen.content.directives import schema, Fields
from grokcore.component import baseclass
from zope.dublincore.property import DCProperty
from zope.interface import implements


class BaseContent(grokcore.content.Model):
    baseclass()
    schema(interfaces.IBaseContent)
    require("zope.ManageContent")

    title = DCProperty('title')

    def __init__(self, **kwargs):
        grokcore.content.Model.__init__(self)
        if kwargs:
            schemas = schema.bind().get(self)
            ifields = Fields(*schemas)
            for key, value in kwargs.items():
                ifield = ifields.get(key)
                if ifield is None:
                    continue
                field = ifield.bind(self)
                field.validate(value)
                field.set(self, value)


class Container(BaseContent, grokcore.content.Container):
    """A dolmen folderish content type.
    """
    baseclass()
    implements(interfaces.IContainer)

    def __init__(self, **kwargs):
        grokcore.content.Container.__init__(self)
        BaseContent.__init__(self, **kwargs)


class OrderedContainer(BaseContent, grokcore.content.OrderedContainer):
    """A dolmen folderish content type with ordered keys.
    """
    baseclass()
    implements(interfaces.IOrderedContainer)

    def __init__(self, **kwargs):
        grokcore.content.OrderedContainer.__init__(self)
        BaseContent.__init__(self, **kwargs)


class Content(BaseContent):
    """A dolmen content type.
    """
    baseclass()
    implements(interfaces.IContent)
