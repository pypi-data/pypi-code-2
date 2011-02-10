"""
Herited schemas example
=======================

  >>> gilgamesh = MesopotamianGod()
  >>> gilgamesh.homecity
  u'Babylon'

  >>> dolmen.schema.bind().get(gilgamesh)
  [<InterfaceClass ...IMythologicalHero>]

The base properties must be inherited, thanks to the schema applier::

  >>> MesopotamianGod.title
  <zope.dublincore.property.DCProperty object at ...>
  
"""
import dolmen.content as dolmen
from zope.schema import TextLine
from grokcore.component import baseclass
from grokcore.content import Container


class IMythologicalHero(dolmen.IBaseContent):
    """A hero that transcended History.
    """
    homecity = TextLine(
        title=u"Name of the home city of the Hero",
        required=True,
        default=u"Babylon")


class Hero(dolmen.Content):
    baseclass()
    dolmen.schema(IMythologicalHero)


class AssyrianHero(Hero):
    baseclass()


class MesopotamianGod(Container, AssyrianHero):
    pass
