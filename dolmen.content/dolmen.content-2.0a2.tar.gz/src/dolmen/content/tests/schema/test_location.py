"""
First grok::

  >>> import dolmen.content.testing
  >>> dolmen.content.testing.grok('dolmen.content.meta',
  ...                             'dolmen.content.tests.schema.test_location')

Content location
================

A ``dolmen.content`` content is locatable. It means it can belong to a
hierarchy and, therefore, hold informations about its current position
or location.

  >>> from zope.location import ILocation

Let's work with a content and a container::

  >>> cave = Cave()
  >>> moody = Tiger()

  >>> ILocation.providedBy(cave)
  True

  >>> ILocation.providedBy(moody)
  True

As we can see, out-of-the-box, ``dolmen.content`` contents provide
ILocation, meaning they have a `__parent__` and `__name__`::

  >>> from zope.interface.verify import verifyObject

  >>> verifyObject(ILocation, cave)
  True

  >>> verifyObject(ILocation, moody)
  True

While working with containment, these attributes will be most
important::

  >>> cave['ugly cat'] = moody

  >>> moody.__name__
  u'ugly cat'

  >>> moody.__parent__
  <dolmen.content.tests.schema.test_location.Cave object at ...>

While deleted from the container, the attributes will be set to None::

  >>> del cave['ugly cat']

  >>> print moody.__name__
  None

  >>> print moody.__parent__
  None

"""

import dolmen.content as dolmen


class Cave(dolmen.Container):
    """A rocky shelter
    """
    dolmen.name('Cave')


class Tiger(dolmen.Content):
    """A wild animal
    """
    dolmen.name('Sabertooth Tiger')
