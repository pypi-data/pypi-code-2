"""Testing that grokcore utilities work under Zope2

  >>> grok.testing.grok(__name__)

  >>> from zope import component
  >>> club = component.getUtility(IFiveClub, 'five_inch')
  >>> IFiveClub.providedBy(club)
  True
  >>> isinstance(club, FiveInchClub)
  True

"""
from zope.interface import Interface
from five import grok

class IFiveClub(Interface):
    pass

class ITinyClub(Interface):
    pass

class FiveInchClub(grok.GlobalUtility):
    grok.implements(IFiveClub, ITinyClub)
    grok.provides(IFiveClub)
    grok.name('five_inch')
