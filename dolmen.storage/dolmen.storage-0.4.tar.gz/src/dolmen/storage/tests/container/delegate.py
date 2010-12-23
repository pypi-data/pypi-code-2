"""
=================
Delegated Storage
=================

`dolmen.storage` provides a couple of useful storage containers. The
second one is a delegated storage component. `DelegatedStorage` is a
component delegating all the container related method to a `storage`,
which is an object implementing `IStorage`.

We first create a DelegatedStorage::

  >>> from dolmen.storage import IStorage, OOBTreeStorage, DelegatedStorage
  
  >>> class MyStorage(DelegatedStorage):
  ...     def __init__(self):
  ...         self.storage = OOBTreeStorage()

  >>> container = MyStorage()


We ensure that the interface is correctly provided::

  >>> IStorage.providedBy(container)
  True
  >>> IStorage.providedBy(container.storage)
  True


In order to enforce the consistency of our declaration, we check the
implementation in depth, using verifyObject::

  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(IStorage, container)
  True


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
  
  >>> for i in container: print repr(i)
  'test'

  >>> 'test' in container
  True

  >>> container.clear()
  >>> len(container)
  0

  >>> container['james'] = object()
  >>> print container.get('james')
  <object object at ...>

  >>> print container.get('judith')
  None

  >>> del container['james']
  >>> print container['james']
  Traceback (most recent call last):
  ...
  KeyError: 'james'

  >>> len(container)
  0


A delegated storage will enforce the check of the object, before
persistence. If a precondition exists, it will be test::

  >>> from zope.interface import Interface, implements
  >>> from zope.container.constraints import contains

  >>> class IComment(Interface):
  ...     pass

  >>> class IComments(Interface):
  ...     contains(IComment)

  >>> class CommentStorage(DelegatedStorage):
  ...     implements(IComments)
  ...     def __init__(self):
  ...         self.storage = OOBTreeStorage()

  >>> class Remark(object):
  ...     implements(IComment)

  >>> class Junk(object):
  ...     pass

  >>> note = Remark()
  >>> junk = Junk()
  >>> comments = CommentStorage()
  >>> comments['trimester1'] = note
  >>> comments['trimester2'] = junk
  Traceback (most recent call last):
  ...
  InvalidItemType: (<dolmen.storage.tests.container.delegate.CommentStorage object at ...>, <dolmen.storage.tests.container.delegate.Junk object at ...>, (<InterfaceClass dolmen.storage.tests.container.delegate.IComment>,))

"""
