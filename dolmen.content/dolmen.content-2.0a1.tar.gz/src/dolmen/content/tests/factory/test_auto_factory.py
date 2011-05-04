"""
First grok::

  >>> import dolmen.content.testing
  >>> dolmen.content.testing.grok('dolmen.content.meta',
  ...                         'dolmen.content.tests.factory.test_auto_factory')

Auto factories
==============

dolmen.content provides a generic factory for each content type
(see 'simple.py' for more details). It is possible to define a
custom factory by adding a class inheriting from dolmen.Factory
in your module or by using the 'factory' directive. The automatic
binding between the content type and the factory works only in the case
we have 1 context and 1 factory in the same module.

For this test, we have a type of object : ICake. We have an implementation :
SweetRoll. And to finish, we have the person that bakes the cake, Joe, the
Factory. In this file, we have only one IContext and only one Factory class.
Therefore, the link between the two will be done automatically :

  >>> from zope.component import getUtility, queryUtility
  >>> from dolmen.content.interfaces import IFactory
  >>> factory = getUtility(IFactory, 'Joe')
  >>> isinstance(factory, Baker)
  True
  >>> factory.description
  u'Sweet rolls baker since 1884'
  >>> factory.getSchema()
  [<InterfaceClass dolmen.content.tests.factory.test_auto_factory.ICake>]

If binded automatically, the generic factory is not registered.

  >>> auto_factory = queryUtility(IFactory,
  ...               'dolmen.content.tests.factory.test_auto_factory.SweetRoll')
  >>> auto_factory is None
  True

We now have a useable factory. We can generate SweetRolls on demand.

  >>> cake = factory()
  >>> ICake.providedBy(cake)
  True

  >>> isinstance(cake, SweetRoll)
  True

  >>> cake.__content_type__
  u'Joes rolled delicacies'

  >>> cake.ingredients
  ['strawberry jam', 'flour', 'eggs']

"""

import dolmen.content as dolmen
from zope.schema import List
from zope.interface import Interface


class ICake(Interface):
    """A sweet eatable object.
    """
    ingredients = List(
        title=u"The ingredients needed to bake the cake.",
        required=True,
        default=[])


class SweetRoll(dolmen.Content):
    """A rolled cake with strawberry jam in it.
    """
    dolmen.schema(ICake)
    dolmen.name(u'Joes rolled delicacies')
    ingredients = ['strawberry jam', 'flour', 'eggs']


class Baker(dolmen.Factory):
    dolmen.name('Joe')
    title = u"Welcome at Joe's bakery"
    description = u"Sweet rolls baker since 1884"
