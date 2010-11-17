# -*- coding: utf-8 -*-
"""ZODB stored data.
"""
from persistent import Persistent
from zope.interface import Interface, implements


class IDataChunk(Interface):
    """A chunk of data.
    """

    def __len__():
        """Returns the length of the data.
        """

    def __str__():
        """Returns the data.
        """


class FileChunk(Persistent):
    """Wrapper for possibly large data
    """
    implements(IDataChunk)

    next = None

    def __init__(self, data):
        self._data = data

    def __getslice__(self, i, j):
        # Deprecated. Is it still necessary ?
        return self._data[i:j]

    def __len__(self):
        data = str(self)
        return len(data)

    def __str__(self):
        next = self.next
        if next is None:
            return self._data

        result = [self._data]
        while next is not None:
            self = next
            result.append(self._data)
            next = self.next

        return ''.join(result)
