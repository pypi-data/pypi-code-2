from persistent import Persistent
from persistent.dict import PersistentDict

from zope.interface import implements

from collective.gsa.interfaces import IGSAQueue


class GSAQueue(Persistent):

    implements(IGSAQueue)

    def __init__(self):
        self.dict=PersistentDict()

    def put(self, url, obj):
        self.dict[url] = obj
        self.dict._p_changed = 1
        
    def update(self, objs):
        self.dict.update(objs)
        self.dict._p_changed = 1

    def purge(self):
        while 1:
            try:
                self.dict.popitem()
            except KeyError, e:
                break

    def get(self):
        if len(self.dict) > 0:
            pos = self.dict.keys()[0]
            obj = self.dict.pop(pos)
            # force changed
            self.dict._p_changed = 1
            return pos, obj

        return None, None
    
    def __len__(self):
        return len(self.dict)

class BasicQueue(object):
    
    def __init__(self):
        self.dict = {}
        
    def put(self, url, obj):
        self.dict[url] = obj

    def update(self, objs):
        self.dict.update(objs)

    def purge(self):
        while 1:
            try:
                self.dict.popitem()
            except KeyError, e:
                break

    def get(self):
        if len(self.dict) > 0:
            pos = self.dict.keys()[0]
            obj = self.dict.pop(pos)
            return pos, obj

        return None, None

    def __len__(self):
        return len(self.dict)
