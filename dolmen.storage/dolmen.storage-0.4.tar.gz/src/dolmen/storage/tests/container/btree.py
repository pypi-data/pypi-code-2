"""
=============
Btree Storage
=============

`dolmen.storage` provides a couple of useful storage containers.
The first one is the BTree. `BtreeStorage` is a very straightforward
component subclassing an OOBTree and implementing `IStorage`.

We first instanciate a BTreeStorage::

  >>> from dolmen.storage import IStorage, OOBTreeStorage
  >>> container = OOBTreeStorage()


We ensure that the interface is correctly provided::

  >>> IStorage.providedBy(container)
  True


In order to enforce the consistency of our declaration, we check the
implementation in depth, using verifyObject::

  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(IStorage, container)
  True


The BTreeStorage is correctly providing what we expect it to
provide. It's an extension of IContainer, exposing the Btree 'clear'
method::

  >>> list(IStorage)
  ['__delitem__', '__getitem__', 'get', 'keys', 'items', 'clear', '__contains__', '__setitem__', '__iter__', 'values', '__len__']


Let's have some basic tests, to check that everything works as
intended::

  >>> container['test'] = 'something'
  >>> len(container)
  1

  >>> container['test']
  'something'

  >>> list(container.values())
  ['something']

  >>> list(container.keys())
  ['test']

  >>> list(container.items())
  [('test', 'something')]
  
  >>> container.clear()
  >>> len(container)
  0
  
"""
