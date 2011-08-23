from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts

from plone.portlets.interfaces import IPortletContext
from plone.app.portlets.portlets.base import Assignment, Renderer
from collective.viewportletmanager.config import VIEW_CATEGORY


class DummyObj(SimpleItem):
    
    def __init__(self, id='1', uid=None):
        self.uid = uid
        self.id = id
    
    def UID(self):
        return self.uid

class NoUIDDummyObj(SimpleItem):
    
    def __init__(self, id='1'):
        self.id = id

class DummyView(object):
    
    __name__ = None
    
    def __init__(self, context, request, name=None):
        self.context = context
        self.request = request
        self.__name__ = name

class DummyPortletContext(object):
    
    implements(IPortletContext)
    
    def __init__(self, context, parent=None):
        self.context = context
        self.parent = parent
    
    def globalPortletCategories(self, placeless=False, view=None):
        if view is None:
            return ()
        uid = 'nouid'
        if hasattr(self.context, 'UID'):
            uid = self.context.UID()
        key = '%s:%s' % (uid, view.__name__)
        return ((VIEW_CATEGORY, key),)

    def getParent(self):
        return self.parent

class DummyStorage(object):
    
    __name__ = None
    
    def __init__(self, data, name=None):
        self.data = data
        self.__name__ = name
    
    def get(self, key, default=None):
        return self.data.get(key, default)

class DummyPortlet(Assignment):
    
    def __init__(self, name=None, available=True):
        self.__name__ = name
        self._avail = available

    @property
    def available(self):
        return self._avail

class DummyPortletRenderer(Renderer):

    adapts(Interface, Interface, Interface, Interface, DummyPortlet)

    def render(self):
        return 'Rendered...'
