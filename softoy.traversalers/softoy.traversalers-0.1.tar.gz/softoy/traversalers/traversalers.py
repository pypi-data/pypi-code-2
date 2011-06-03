# -*- coding: utf-8 -*-
"""
traversables.py
2010-5-10

Changes:
contained object's id start from 0 for convenience
remove data attriute on Container
"""

from persistent.mapping import PersistentMapping
from persistent import Persistent
from BTrees import IOBTree
import transaction

class RootModel(PersistentMapping):
    __parent__ = None
    __name__ = ''

    def add_container(self, cont, name=None):
        if name:
            cont_name = name
        else:
            cont_name = cont.__class__.__name__
        
        if cont_name not in self:
            self[cont_name] = cont(cont_name, self)
            return self[cont_name]


class GraphNode(Persistent):
    __name__ = ''
    __parent__ = ''


class GraphNodeLazy(GraphNode):
    def __call__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent
        return self


class Container(GraphNodeLazy):
    def __init__(self):
        self.__parent__ = None
        self. __name__ = ''
        self.data = PersistentMapping()
        
    def __getitem__(self, key):
        return self.data[key]
        
    def __setitem__(self, key, value):
        self.data[key] = value
        
    def items(self):
        return self.data.items()
        
    def keys(self):
        return self.data.keys()
        
    def values(self):
        return self.data.values()
        
    def __len__(self):
        return len(self.data)
        
    def __call__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent
        return self

    def add_container(self, cont):
        cont_name = cont.__class__.__name__
        if cont_name not in self.data:
            self.data[cont_name] = cont(cont_name, self)
            return self[cont_name]


class Settings(Container):
    def __init__(self):
        super(Settings, self).__init__()
        

class ModelContainer(Container):
    def __init__(self):
        super(ModelContainer, self).__init__()

    def auto_key(self):  # first key  is zero
        if len(self.data) == 0:
            return 0
        else:
            return max(self.keys()) + 1

    # CRUD - if error then rollback and return None
    def create(self, ob):
        setattr(ob, '_id', self.auto_key())
        setattr(ob, '__name__', ob._id)
        setattr(ob, '__parent__', self)
        txpoint = transaction.savepoint()
        try:
            self[ob._id] = ob
            return ob._id
        except:
            txpoint.rollback()

    def retrieve(self, _id):
        return self.get(_id)

    def update(self, ob):  # if ob have not valid id then return None
        if not self.has_valid_id(ob):
            return
        if ob._id in self.data:
            txpoint = transaction.savepoint()
            try:
                self[ob._id] = ob
                return ob._id
            except:
                txpoint.rollback()

    def delete(self, _id):
        if _id in self.data:
            txpoint = transaction.savepoint()
            try:
                del self.data[_id]
                return _id
            except:
                txpoint.rollback()

    def is_valid_id(self, _id):
        return isinstance(_id, (int, long)) and _id >= 0

    def has_valid_id(self, ob):
        try:
            _id = getattr(ob, '_id')
        except AttributeError:
            return
        return self.is_valid_id(ob._id)

    def length(self):
        return len(self)


class SmartModel(GraphNode):
    _fields_ = ['_id']
    
    def __init__(self, **kw):
        self.__name__ = ''
        self.__parent__ = ''
        
        for field in self._fields_:
            setattr(self, field, kw.get(field))

    def __repr__(self):
        return u', '.join(
            [u'%s:%s' % (field, getattr(self, field)) for field in self._fields_]
            )


class SequenceModel(GraphNodeLazy):
    def __init__(self):
        self.data = IOBTree()


class Chrono(Container):
    def __init__(self):
        super(Chrono, self).__init__()
    
    def get_sub(self, factor):
        if factor not in self:
            self[factor] = nested_model()
            self[factor].factor = factor
        return self[factor]
    
    def add(self, entry, factor):
        submodel = self.get_sub(factor)
        if self.factor_name == 'day':
            return submodel.create(entry)
        else:
            return submodel.add(entry, factor)


class Daily(Chrono):
    factor_name = 'day'
    nested_model = ModelContainer
        
    def __init__(self):
        super(Daily, self).__init__()
        self.factor = None


class Monthly(Chrono):
    factor_name = 'month'
    nested_model = Daily
    
    def __init__(self):
        super(Monthly, self).__init__()
        self.factor = None


class Yearly(Chrono):
    factor_name = 'year'
    nested_model = Monthly
    
    def __init__(self):
        super(Yearly, self).__init__()
        self.factor = None









