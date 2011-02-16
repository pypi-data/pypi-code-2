"""
Instanciation
=============

A dolmen.content Content only needs a name to be fully useable.

  >>> mongo = Dummy()
  >>> mongo.__content_type__
  u'DummyContent'

  >>> from grokcore.component.interfaces import IContext
  >>> IContext.providedBy(mongo)
  True


Schema
======

This content is getting a base interface and a base schema.
It means that the attributes are set by default on the content type.
Of course, the basic fields validations are respected.

  >>> IDummySchema.providedBy(mongo)
  True
  >>> mongo.title
  u''
  >>> mongo.title = 'a vast bowl of pus'
  Traceback (most recent call last):
  ...
  WrongType: ('a vast bowl of pus', <type 'unicode'>, 'title')

  >>> mongo.title = u'Oh... it makes me mad... mad!'
  >>> mongo.title
  u'Oh... it makes me mad... mad!'


Factory
=======

In order to get an abstract and generic way to handle the content types,
`dolmen.content` provides a factory system that permits to instanciate your
objects.

Further, if no factory is explicitly declared, one is automatically generated
and registered, using the package path and class name as an identifier.

  >>> from dolmen.content import IFactory
  >>> from zope.component import getUtility
  >>> myfactory = getUtility(IFactory,
  ...                        name='dolmen.content.tests.overview.simple.Dummy')

  >>> myfactory.factory
  <class 'dolmen.content.tests.overview.simple.Dummy'>

  >>> myfactory.getSchema()
  [<InterfaceClass dolmen.content.tests.overview.simple.IDummySchema>]

The factory describes the generated content::

  >>> myfactory.name
  'DummyContent'

  >>> myfactory.title
  'A Dummy content'

  >>> myfactory.description
  'A very dumb and dull content.'

Finally, the factory provides the name of the view serving as an add
form to add the content through the web::

  >>> myfactory.addform
  u'dolmen.add'

  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(IFactory, myfactory)
  True

Content type with no directives
-------------------------------

  >>> infoless = getUtility(IFactory,
  ...              name='dolmen.content.tests.overview.simple.InfoLess')

  >>> infoless.name
  'InfoLess'

  >>> infoless.description
  u''

  >>> infoless.title
  u''

  >>> infoless.addform
  u'dolmen.add'

  >>> verifyObject(IFactory, infoless)
  True

"""

import dolmen.content as dolmen
from zope.schema import TextLine
from zope.interface import Interface


class IDummySchema(Interface):
    title = TextLine(
        title=u"Title",
        required=True,
        default=u'')


class Dummy(dolmen.Content):
    """A very simple content
    """
    dolmen.name('DummyContent')
    dolmen.title('A Dummy content')
    dolmen.description('A very dumb and dull content.')
    dolmen.schema(IDummySchema)


class InfoLess(dolmen.Content):
    pass
