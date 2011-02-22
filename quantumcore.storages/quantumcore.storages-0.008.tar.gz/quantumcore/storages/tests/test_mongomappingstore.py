from quantumcore.storages.exc import DuplicateKey
import py

# skip this test if pymongo cannot be imported
pymongo = py.test.importorskip("pymongo")

class TestMongoMappingStore(object):
    
    def test_add_and_retrieve(self, mongostore):
        entry = {'foo' : 'bar'}                 
        k = mongostore.add(entry)
        
        result = mongostore[k]
        assert result['foo']=='bar'
        
    def test_add_duplicate(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)

        entry['_id'] = k # duplicate the key
        py.test.raises(DuplicateKey, mongostore.add, entry)
        
    def test_unsafe_add_duplicate(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)
        
        entry['_id'] = k # duplicate the key
        entry['foo'] = 'bar2'
        k2 = mongostore.add(entry, safe=False)
        assert k==k2
        
        entry = mongostore[k]
        assert entry['foo']=='bar' # the second add() is gone        
        
    def test_get_default(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)
        
        entry = mongostore.get("nothing", 123)
        assert entry==123
        
    def test_getitem_with_unknown_key(self, mongostore):
        py.test.raises(KeyError, lambda: mongostore['foobar'])
        
    def test_get(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)
        assert mongostore.get(k, "foobar")['foo'] == 'bar'
        
    def test_update(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)
        
        entry = mongostore[k]
        entry['foo']='bar2'
        mongostore.update(entry)
        
        entry = mongostore[k]
        assert entry['foo']=='bar2'

    def test_update_without_key(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)
        
        py.test.raises(KeyError, lambda: mongostore.update(entry))
        
    def test_delete(self, mongostore):
        entry = {'foo' : 'bar'} 
        k = mongostore.add(entry)
        mongostore.delete(k)
        
        assert mongostore.get(k) is None
        
    def test_delete_with_unkown_key(self, mongostore):
        mongostore.delete(u'blafasel') # nothing happens ;-)

    def test_find(self, mongostore):
        entry = {'footest' : u'bar'} 
        k = mongostore.add(entry)
        
        entries = mongostore.find({'footest' : u"bar"})
        l = len(list(entries))
        assert l==1
        

    