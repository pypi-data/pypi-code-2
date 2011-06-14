# -*- coding: utf-8 -*-

from persistent import Persistent
from cromlech.container.contained import Contained

from dolmen.content.directives import schema
from dolmen.content.utils import bootstrap_object
from dolmen.content.interfaces import IContent, IContainer, IOrderedContainer
from dolmen.container.components import BTreeContainer, OrderedBTreeContainer

from grokcore.security import require
from grokcore.component import baseclass
from grokcore.component.interfaces import IContext
from zope.interface import implements


class Model(Contained):
    baseclass()
    implements(IContext, IContent)
    require("zope.ManageContent")

    def __init__(self, **kwargs):
        Contained.__init__(self)
        if kwargs:
            schemas = schema.bind().get(self)
            if schemas:
                bootstrap_object(self, *schemas, **kwargs)


class Content(Model, Persistent):
    baseclass()

    def __init__(self, **kwargs):
        Persistent.__init__(self)
        Model.__init__(self, **kwargs)


class Container(Model, BTreeContainer):
    """A dolmen folderish content type.
    """
    baseclass()
    implements(IContainer)

    def __init__(self, **kwargs):
        BTreeContainer.__init__(self)
        Model.__init__(self, **kwargs)


class OrderedContainer(Model, OrderedBTreeContainer):
    """A dolmen folderish content type with ordered keys.
    """
    baseclass()
    implements(IOrderedContainer)

    def __init__(self, **kwargs):
        OrderedBTreeContainer.__init__(self)
        Model.__init__(self, **kwargs)


__all__ = ['Model', 'Content', 'Container', 'OrderedContainer']
