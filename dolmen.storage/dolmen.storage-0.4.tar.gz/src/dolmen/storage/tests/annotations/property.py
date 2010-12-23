"""
===========================
Annotation storage property
===========================

Often, when we want to extend a component, we need to store
values. Zope provides a very flexible mechanism called `annotations`
which permits us to add information on an object, by following a very simple
API.

In `dolmen.storage` we build on top of the annotation mechanism to provide a
very transparent way to store new values as properties.


Getting started
---------------

We boostrap our project by importing the basic dependencies and
initializing the annotation component::

  >>> from zope.annotation.attribute import AttributeAnnotations
  >>> from zope.component import provideAdapter
  >>> provideAdapter(AttributeAnnotations)

Then, using Grok, we grok the module to register the components::

  >>> import grokcore.component as grok
  >>> from grokcore.component import testing
  >>> testing.grok(__name__)


Annotatable object
------------------

Let's go through a simple example to demonstrate the behavior of an
annotation property. We are going to implement a document that
can be commented.

First, let's declare our document class::

  >>> from zope.interface import implements
  >>> from zope.annotation.interfaces import IAttributeAnnotatable

  >>> class Document(object):
  ...    '''A very basic document
  ...    '''
  ...    implements(IAttributeAnnotatable)
  ...   
  ...    def __init__(self, body):
  ...        self.body = body

Here, our document class implement IAttributeAnnotatable, meaning it
is elegible for an attribute annotation, which stores the annotation
on the `__annotations__` attribute.


Declaring the API
-----------------

The document class is defined. However, We want to add a
comment and a rating value on it. We want this to be clear and provide
an explicit API.

The API we want to expose looks like this::

  >>> from zope.interface import Interface
  >>> from zope.schema import TextLine, Int

  >>> class IComment(Interface):
  ...    remark = TextLine(title=u'A comment', default=u'N/A')
  ...    rating = Int(title=u'A mark', default=0)


Annotation property
-------------------

To make this API useable, we implement it into an *Adapter* (a pluggable
component). In this *Adapter*, the attributes defined in the API will be
annotation properties.

An annotation property will provide a simple way to access a value
stored in the annotation. Further more, it will provide a validation on
the value attribution and a default value on the retrieval.

Let's create this adapter::

  >>> from dolmen.storage import AnnotationProperty

  >>> class Commenting(grok.Adapter):
  ...    grok.context(Document)
  ...    grok.implements(IComment)
  ...
  ...    remark = AnnotationProperty(IComment['remark'], storage='simple')
  ...    rating = AnnotationProperty(IComment['rating'], storage='simple',
  ...                                name='mark')


This is very close to a `zope.schema.fieldproperty.FieldProperty`
property. Beside the field object, two keyword arguments can be given
: `storage` and `name`. `storage` is the name of the
`dolmen.storage.IDelegatedStorage` component in charge of the
containment and `name` is the name of key we want to use in the
annotation to persist this particular value.


Delegated containment
---------------------

In order to keep everything flexible and specialized, the storage is
handled by an adapter providing `IDelegatedStorage`.

In the `Commenting` adapter, the properties specify 'simple' as a
storage name. Let's implement this storage component::

  >>> from dolmen.storage import AnnotationStorage

  >>> class SimpleStorage(AnnotationStorage):
  ...    grok.name('simple')

That's all!


Testing the commenting system
-----------------------------

Let's Grok the components to make then available::

  >>> testing.grok_component('simplestorage', SimpleStorage)
  True
  >>> testing.grok_component('commenting', Commenting)
  True

Now, we instantiate a Document and adapt the new object. The adapted object
now provides our Commenting API::

  >>> thesis = Document(u'A thesis about Mammoth')
  >>> commenting = IComment(thesis)

We print the default values of our fields::

  >>> print commenting.remark
  N/A
  >>> print commenting.rating
  0

Let's set new values::
  
  >>> commenting.remark = u'A good effort. Continue like this.'
  >>> commenting.rating = 13

We print our values to check that everything has been stored correctly::

  >>> print commenting.remark
  A good effort. Continue like this.
  >>> print commenting.rating
  13

The property checks the validity of the value::

  >>> commenting.remark = ['A', 'B']
  Traceback (most recent call last):
  ...
  WrongType: (['A', 'B'], <type 'unicode'>, 'remark')

Lastly, we can check how the values are stored::

  >>> annotations = thesis.__annotations__
  >>> list(annotations.keys())
  ['simple']
  >>> list(annotations.get(u'simple').keys())
  ['mark', 'remark']

"""
