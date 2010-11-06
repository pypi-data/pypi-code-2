"""
Herited schemas example
=======================

  >>> gilgamesh = MesopotamianGod()
  >>> gilgamesh.homecity
  u'Babylon'

  >>> dolmen.schema.bind().get(gilgamesh)
  [<InterfaceClass ...IMythologicalHero>]
  
"""
import dolmen.content as dolmen
from zope.interface import Interface
from zope.schema import TextLine
from grokcore.component import baseclass
from grokcore.content import Container


class IMythologicalHero(Interface):
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
