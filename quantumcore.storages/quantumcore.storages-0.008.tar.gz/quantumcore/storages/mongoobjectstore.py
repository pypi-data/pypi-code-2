
import datetime, time
import copy
import pymongo
from pymongo import ASCENDING, DESCENDING

from mongomappingstore import MongoMappingStore

class ObjectInvalid(Exception):
    """raise this in case verify() fails. You can give it a message, too"""
    
    def __init__(self, msg = ''):
        self.msg = msg
        
    def __str__(self):
        return "ObjectInvalid Error: %s" %self.msg
    
    __repr__=__str__

class Model(object):
    """a data model"""
    
    # this is the list of attributes to store. There is no type etc. associated
    _attribs = ['_id']
    _defaults = {} # default values
    
    def __init__(self, _id=None, _store = None, **kwargs):
        """initialize the database object class. """

        self._id = _id

        # filter out those attribs which we don' store
        data = copy.copy(self._defaults)
        data.update(kwargs)
        for a,v in data.items():
            if a in self._attribs:
                setattr(self, a, data[a])

        self._store = _store
        self._after_init()

    def _after_init(self):
        """hook for doing something after initialization"""
        pass
                
    def _to_dict(self):
        """serialize this object to a dictionary"""
        d={}
        for attrib in self._attribs:
            if attrib=='_id' and self._id is None:
                continue
            d[attrib] = getattr(self, attrib, u'')
        return d
            
    @classmethod
    def from_dict(cls, d, store):
        """create an entry from the data given in d"""
        d = dict([(str(a),v) for a,v in d.items()])
        d['_store']=store
        return cls(**d)
        
    def set_id(self, id_):
        self._id = id_

    def get_id(self):
        return self._id

    id = property(get_id, set_id)
        

class MongoObjectStore(object):
    """this store stores ``DataObject``s in a MongoDB."""
    
    data_class = Model
    
    def __init__(self, database, collection_name):
        """initialize the storage with a database to use"""
            
        self.database = database
        self.collection_name = collection_name
        self.collection = database[collection_name]
        
    def clean(self):
        """clean the database"""
        self.database.drop_collection(self.collection_name)        
        self.coll = self.database[self.collection_name]
            
    def put(self, obj, safe=True):
        """add an entry to the database"""
        data = obj._to_dict()
        return self.collection.insert(data, safe=safe)
        
    def find(self, query={}, 
                   sort_on=None, 
                   sort_order=pymongo.ASCENDING,
                   limit=10,
                   offset=0):
        """return some entries based on the query"""
        results = self.collection.find(query)
        if sort_on is not None:
            results.sort(sort_on, sort_order)
        results = results[offset:limit+offset]
        objects = [self.data_class.from_dict(result, self) for result in results]
        return objects

    def count(self, query={}):
        """return the amount of matching images"""
        return self.collection.find(query).count()
        
    def get(self, _id):
        """return an entry by id"""
        results = self.find({'_id': _id})
        if len(results)==0:
            return None
        return results[0]

    __getitem__ = get
    
    def update(self, obj, safe=True):
        """update an object"""
        data = obj._to_dict()
        self.collection.save(data, safe=safe)
        return data # return the raw data for further inspection

    def delete(self, _id, safe=True):
        """delete an object"""
        return self.collection.remove({'_id':_id}, safe=safe)

    def all(self):
        """return an iterator which returns all objects"""
        all = self.collection.find()

        class ObjectIterator(object):

            def __init__(self, items, store):
                self.items = items
                self.store = store

            def __iter__(self):
                return self

            def next(self):
                return self.store.data_class.from_dict(self.items.next(), self.store)

        return ObjectIterator(all, self)

