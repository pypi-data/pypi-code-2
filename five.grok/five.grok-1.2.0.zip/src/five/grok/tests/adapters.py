"""Testing that grokcore adapters work under Zope2

  >>> grok.testing.grok(__name__)

  >>> from OFS.SimpleItem import SimpleItem
  >>> item = SimpleItem()
  >>> item.id = 'item'
  >>> adapted = IId(item)
  >>> isinstance(adapted, SimpleItemIdAdapter)
  True
  >>> IId.providedBy(adapted)
  True
  
  >>> adapted.id()
  'item'

"""
from zope.interface import Interface
from five import grok
from OFS.interfaces import ISimpleItem

class IId(Interface):
    
    def id():
        """Returns the ID of the object"""

class SimpleItemIdAdapter(grok.Adapter):
    grok.implements(IId)
    grok.context(ISimpleItem)

    def id(self):
        return self.context.getId()
