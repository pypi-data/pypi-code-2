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
from zope.interface import Interface
from zope.schema import Choice


class IViking(Interface):
    """Defines a Norseman
    """
    rank = Choice(
        title=u"Rank of the viking warrior",
        default=u"Jarl",
        values=[u"Bondi", u"Hersir", u"Jarl", u"Einherjar"])


class Ynglingar(dolmen.content.Content):
    dolmen.content.schema(IViking)


class JomsWarrior(dolmen.content.Content):
    dolmen.content.schema(IViking)
    rank = u"Bondi"
