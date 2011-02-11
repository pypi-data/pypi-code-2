"""
One schema example
==================

Conan is a simple Barbarian. Thinking is an everyday challenge for him.
While he's not punching camels, he's resting or drinking in a tavern.
Therefore, only one schema can define him pretty good :

  >>> conan = Barbarian()
  >>> IBarbarian.providedBy(conan)
  True
  >>> dolmen.IContent.providedBy(conan)
  True
 
Of course, our Barbarian is an IBarbarian but still a IContent.
It still has the title and __content_type__ attributes. It also has the
attributes defined in the IBarbarian interface, set by default.

  >>> conan.nickname
  u'The Barbarian'
  >>> conan.kills
  100

"""

import dolmen.content as dolmen
from zope.interface import Interface
from zope.schema import TextLine, Int

    
class IBarbarian(Interface):
    """A barbarian. Usually only wearing a leather underpants.
    """
    kills = Int(
        title=u"Kills !",
        default=100)

    nickname = TextLine(
        title=u"Nickname",
        default=u"The Barbarian")


class Barbarian(dolmen.Content):
    """A barbarian content
    """
    dolmen.name('male')
    dolmen.schema(IBarbarian)
