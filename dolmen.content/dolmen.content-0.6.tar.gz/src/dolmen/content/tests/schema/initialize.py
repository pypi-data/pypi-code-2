"""
Values initialization
=====================

A `dolmen.content` content type is defined by its schema. When a schema
is applied on a content type, the fields are bootstrapped on the class,
and the instance of the class uses the default values.

  >>> mcDuff = Thane()
  >>> mcDuff.age
  0
  >>> mcDuff.thanehood
  []

It's possible, however, to give initial values to the constructor::

  >>> mcBeth = Thane(age=35, thanehood=[u'Glamis', u'Cawdor'])
  >>> mcBeth.age
  35
  >>> mcBeth.thanehood
  [u'Glamis', u'Cawdor']

The values are verified according to the schema. Elements that are not
part of the schema are currently skipped::

Providing a wrong type or unaccepted value will raise an error::

  >>> lennox = Thane(age='45')
  Traceback (most recent call last):
  ...
  WrongType: ('45', (<type 'int'>, <type 'long'>), 'age')

Providing a non-existing field value will do nothing::

  >>> lady = Thane(madness=True)
  >>> print lady
  <dolmen.content.tests.schema.initialize.Thane object at ...>

"""
import dolmen.content
from zope.schema import Int, List, TextLine


class IThane(dolmen.content.IBaseContent):
    """Defines a Scotland's Thane
    """
    age = Int(
        title=u"Age of the Thane",
        default=0)

    thanehood = List(
        title=u"Names of the thane's domains",
        value_type=TextLine(),
        default=[],
        required=True)


class Thane(dolmen.content.Content):
    dolmen.content.schema(IThane)
