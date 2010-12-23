# -*- coding: utf-8 -*-

from zope.schema import Object
from zope.container.interfaces import IContainer


class IStorage(IContainer):
    """A storage item handles the persistence of a given item.
    A storage has three main actions : store, retrieve, delete.
    """

    def clear():
        """Clears the content of the storage. Returns None.
        """


class IDelegatedStorage(IStorage):
    """A storage item handles the persistence of a given item.
    A storage has three main actions : store, retrieve, delete.
    """

    storage = Object(
        title=u"Storage container",
        description=u"A container to delegate the storage.",
        schema=IStorage,
        default=None,
        )
