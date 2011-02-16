# -*- coding: utf-8 -*-

import grokcore.content
from dolmen.content import interfaces, require
from dolmen.content.directives import schema, Fields
from grokcore.component import baseclass
from zope.interface import implements


class Content(grokcore.content.Model):
    baseclass()
    require("zope.ManageContent")
    implements(interfaces.IContent)

    def __init__(self, **kwargs):
        grokcore.content.Model.__init__(self)
        if kwargs:
            schemas = schema.bind().get(self)
            if schemas:
                ifields = Fields(*schemas)
                for key, value in kwargs.items():
                    ifield = ifields.get(key)
                    if ifield is None:
                        continue
                    field = ifield.bind(self)
                    field.validate(value)
                    field.set(self, value)


class Container(Content, grokcore.content.Container):
    """A dolmen folderish content type.
    """
    baseclass()
    implements(interfaces.IContainer)

    def __init__(self, **kwargs):
        grokcore.content.Container.__init__(self)
        Content.__init__(self, **kwargs)


class OrderedContainer(Content, grokcore.content.OrderedContainer):
    """A dolmen folderish content type with ordered keys.
    """
    baseclass()
    implements(interfaces.IOrderedContainer)

    def __init__(self, **kwargs):
        grokcore.content.OrderedContainer.__init__(self)
        Content.__init__(self, **kwargs)
