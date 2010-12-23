"""
============================
Annotation storage container
============================

Getting started
===============

We boostrap out project by importing the basic dependencies and
initializing the annotation component::

  >>> from zope.annotation.attribute import AttributeAnnotations
  >>> from zope.component import provideAdapter
  >>> provideAdapter(AttributeAnnotations)

Then, grokking the module will allow us to register our components
using Grok::

  >>> import grokcore.component as grok
  >>> from grokcore.component import testing
  >>> testing.grok(__name__)

We first define our Content. We make it IAttributeAnnotation to be
able to create annotations::

  >>> from zope.annotation.interfaces import IAttributeAnnotatable

  >>> class Mammoth(object):
  ...    '''A furry creature
  ...    '''
  ...    grok.implements(IAttributeAnnotatable)
  >>> manfred = Mammoth()


storage components
==================

An annotation storage is a specialization of a delegated storage. In
this compinent, the `storage` attribute returns a container written in
an annotation.

  >>> from dolmen.storage import AnnotationStorage, IDelegatedStorage


Unnamed storage
---------------

An annotation storage can be defined as following::

  >>> class MyStorage(AnnotationStorage):
  ...     pass

An annotation storage implements the dolmen.storage.IDelegatedStorage
interface::

  >>> from zope.interface import verify
  >>> verify.verifyClass(IDelegatedStorage, MyStorage)
  True

This example is the most basic declaration. It will use default values::

  >>> mystorage = MyStorage(manfred)
  >>> mystorage.storage.__name__
  '++storage++dolmen.default'


Named storage
-------------

An annotation storage can be named. The name will define the
annotation key used to persist the container.

  >>> class NamedStorage(AnnotationStorage):
  ...    grok.name('some.name')

  >>> named_storage = NamedStorage(manfred)
  >>> named_storage.storage.__name__
  '++storage++some.name'


Custom storage container
------------------------

An annotation storage can define a custom container, to be written
down in annotation and serve as a delegation container. If none is
provided, a `dolmen.storage.OOBTreeStorage` will be used::

  >>> named_storage.storage
  <dolmen.storage.container.OOBTreeStorage object at ...>

To define your own container class, use the `_factory` attribute::

  >>> from dolmen.storage import IOBTreeStorage
  >>> class CustomStorage(AnnotationStorage):
  ...     grok.name('custom')
  ...     _factory = IOBTreeStorage

  >>> custom = CustomStorage(manfred)
  >>> custom.storage
  <dolmen.storage.container.IOBTreeStorage object at ...>


Storage adapters
----------------

The components defined above can be registered as adapters providing
`dolmen.storage.IDelegatedStorage`::

  >>> testing.grok_component('named', NamedStorage)
  True

Once it's grokked, we can query it as an adapter::

  >>> from zope.component import getAdapter

  >>> james = Mammoth()
  >>> storage = getAdapter(james, IDelegatedStorage, "some.name")
  >>> storage
  <dolmen.storage.tests.annotations.storage.NamedStorage object at ...>

We can check the state of the annotations::

  >>> storage.storage['test'] = object()
  >>> list(james.__annotations__.keys())
  ['some.name']

"""
