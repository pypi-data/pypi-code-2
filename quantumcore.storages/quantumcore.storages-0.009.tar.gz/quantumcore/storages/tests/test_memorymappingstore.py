from quantumcore.storages.exc import DuplicateKey
import py

class TestMemoryMappingStore(object):
    
    def test_add_and_retrieve(self, md):
        entry = {'asset_id' : 1, 
                 'foo' : 'bar'}
                 
        md.add(entry)
        
        result = md[1]
        assert result['foo']=='bar'
        
    def test_add_duplicate(self, md):
        entry = {'asset_id' : 1, 
                 'foo' : 'bar'}
             
        md.add(entry)
        py.test.raises(DuplicateKey, md.add, entry)
        
    def test_add_without_key(self, md):
        entry={1:2}
        k = md.add(entry)
        assert k is not None
        assert len(k)==36 # not really black box but that's ok (uuid length)
    
    def test_add_and_retrieve_without_key(self, md):
        entry={1:2}
        k = md.add(entry)
        e = md[k]
        assert e is not None
        assert e[1]==2
        assert e['asset_id']==k
        
    def test_delete(self, md):
        entry = {'asset_id' : 1, 
                 'foo' : 'bar'}

        md.add(entry)
        md.delete(1)
        py.test.raises(KeyError, lambda: md[1])
        
    def test_update(self, md):
        entry={1:2}
        k = md.add(entry)
        e = md[k]
        e[1]=3
        e[2]=4
        md.update(e)
        
        e2=md[k]
        assert e2[1]==3
        assert e2[2]==4
        
        