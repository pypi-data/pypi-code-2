from exc import KeyGenerationError, DuplicateKey
import uuid
import copy

class MemoryMappingStore(object):
    """a data storage in memory. Simply stores dictionaries. It's not fast and it's
    not persistent so don't use it in production."""
    
    def __init__(self, unique_key):
        """initialize the storage by defining the unique key to use"""
        
        self.unique_key = unique_key
        self.entries = {}
        
    def add(self, entry):
        """add an entry"""
        entry = copy.copy(entry)
        uk = self.unique_key
        if entry.has_key(uk):
            k = entry[uk]
        else:
            success = False
            for i in range(1000):
                k = entry[uk] = unicode(uuid.uuid4())
                if k not in self.entries.keys():
                    success = True
                    break
            if not success:
                raise KeyGenerationError("1000 collisions, giving up")

        if k in self.entries.keys():
            raise DuplicateKey(k)
        self.entries[k] = entry
        return k
        
    def __getitem__(self, k):
        """return an entry"""
        return self.entries[k]
        
    def delete(self, k):
        """delete the entry with unique key k"""
        del self.entries[k]
        
    def update(self, e):
        """update an entry"""
        uk=self.unique_key
        if uk not in e.keys():
            raise KeyError(uk)
        k=e[uk]
        self.entries[k] = e
        return e
        
    def find(self, query):
        """search for entries with a query dict"""
        results = []
        for entry in self.entries:
            found=True
            for a in query.keys():
                if entry[a]!=query[a]:
                    found=False
                    break
            if found:
                results.append(entry)
        return results
