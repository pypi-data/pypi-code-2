from rum.exceptions import BadId
from itertools import count

class ModelType(type):
    _stores = {}
    def __new__(meta, name, bases, dct):
        store = dct.setdefault('_%s__store'%name, {})
        dct.setdefault('_%s__counter'%name, count(0))
        new = type.__new__(meta, name, bases, dct)
        meta._stores[new] = store
        return new

def clear_all():
    for store in ModelType._stores.itervalues():
        store.clear()

class Model(object):
    __metaclass__ = ModelType
    id = None

    def __init__(self, **kw):
        self.__dict__.update(**kw)

    @classmethod
    def get(cls, id):
        try:
            id = int(id)
        except:
            raise BadId("%r is not a valid id for this kind of model"%id)
        return cls.__store[int(id)]

    @classmethod
    def select(cls, query):
        return filter(query, cls.__store.itervalues())

    def save(self):
        cls = self.__class__
        self.id = cls.__counter.next()
        cls.__store[self.id] = self

    def delete(self):
        cls = self.__class__
        del cls.__store[self.id]
        
    a="a"
    b="b"
    c="c"
class Person(Model):
    pass

class Address(Model):
    pass

