"""
Values preservation
===================

A `dolmen.content` content type can provide values described in the
schema at the class level. These values are thus preserved::

  >>> harfagri = Ynglingar()
  >>> harfagri.rank
  u'Jarl'

  >>> gormsson = JomsWarrior()
  >>> gormsson.rank
  u'Bondi'

"""

import dolmen.content
from zope.schema import Choice
from zope.schema.fieldproperty import FieldProperty


class IViking(dolmen.content.IBaseContent):
    """Defines a Scotland's Thane
    """
    rank = Choice(
        title=u"Rank of the viking warrior",
        default=u"Jarl",
        values=[u"Bondi", u"Hersir", u"Jarl", u"Einherjar"])


class Ynglingar(dolmen.content.Content):
    dolmen.content.schema(IViking)
    rank = FieldProperty(IViking['rank'])


class JomsWarrior(dolmen.content.Content):
    dolmen.content.schema(IViking)
    rank = u"Bondi"
