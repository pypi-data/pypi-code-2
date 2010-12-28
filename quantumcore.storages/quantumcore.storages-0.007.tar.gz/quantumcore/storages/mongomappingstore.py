from exc import KeyGenerationError, DuplicateKey
import uuid
import copy
import pymongo

class MongoMappingStore(object):
    """a mapping store for storing documents in MongoDB."""
    
    def __init__(self, coll):
        """initialize the storage by defining the unique key to use. ``coll`` is
        a ``PyMongo`` ``Collection`` instance."""
        self.coll = coll
        
    def add(self, entry, safe=True):
        """add an entry. If ``safe`` is ``True`` an ``DuplicateKey`` will be raised in case
        the key already exists in the collection, otherwise the entry will be overwritten"""
        entry = copy.copy(entry)
        try: 
            k = self.coll.insert(entry, safe=safe)
        except pymongo.errors.DuplicateKeyError, e:
            raise DuplicateKey(str(entry['_id']))
        return k

    def __getitem__(self, k):
        """return an entry identified by key ``k`` or raise a ``KeyError`` if it does 
        not exists"""
        r = self.coll.find_one({'_id':k})
        if r is None:
            raise KeyError(k)
        return r
        
    def get(self, k, default=None):
        """return an entry identified by key ``k`` and optionally give a ``default`` value
        which is returned if the entry with key ``k`` does not exist. ``default`` defaults
        to ``None``."""
        r = self.coll.find_one({'_id':k})
        if r is None:
            return default
        return r
                
    def update(self, e):
        """update a single entry"""
        self.coll.update({'_id': e['_id']}, e)
        
    def delete(self, k, safe=False):
        """delete the entry with key ``k``"""
        self.coll.remove({'_id': k}, safe=safe)
        
    def find(self, query):
        """search for entries with a query dict"""
        return self.coll.find(query)
