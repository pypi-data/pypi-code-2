from quantumcore.storages import AttributeMapper
import py.test

def test_attribute_retrieve():
    a=AttributeMapper()
    a['foo']='bar'
    assert a.foo=='bar'
    
def test_attribute_set():
    a=AttributeMapper()
    a.foo = "Bar"
    assert a['foo']=='Bar'
    
def test_retrieve_non_existing_attribute():
    a=AttributeMapper()
    py.test.raises(AttributeError, lambda: a.foo)
