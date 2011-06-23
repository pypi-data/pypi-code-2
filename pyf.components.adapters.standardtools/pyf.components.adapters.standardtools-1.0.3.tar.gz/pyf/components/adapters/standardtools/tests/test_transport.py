from pyf.componentized.core import Manager
from pyf.componentized import ET
from pyf.transport import Packet

import os
import random
from operator import attrgetter

# dummy data holder
from pyf.components.adapters.standardtools import tests

DATADIR = "pyf/components/adapters/standardtools/tests/data" 

class DummyObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
            
    def __eq__(self, other_obj):
        if not hasattr(other_obj, '__dict__'):
            return False
        
        for k in set(other_obj.__dict__.keys() + self.__dict__.keys()):
            if getattr(self, k, None) != getattr(other_obj, k, None):
                return False
        
        return True

def test_missing_attribute():
    """Test a packet encoder with some missing attributes."""
    test_file = "missing_attributes.xml"
    
    data_list = [DummyObject(titi=i, toto=i*2, blah="hoho") for i in range(100)]

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    
    error_happened = False
    try:
        output_files = manager.process("main", params=dict(data=data_list))
    except AttributeError:
        error_happened = True
        
    assert error_happened, "An AttributeError should have occured"
    
def test_allow_missing_attribute():
    """Test a packet encoder with some missing attributes and allow_missing_attributes."""
    test_file = "allow_missing_attributes.xml"
    
    data_list = [DummyObject(titi=i, toto=i*2, blah="hoho") for i in range(100)]

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    
    error_happened = False
    try:
        output_files = manager.process("main", params=dict(data=data_list))
    except AttributeError:
        error_happened = True
        
    assert error_happened is False, "An AttributeError shouldn't have occured"
    
    assert len(tests.missing_attributes_items) == len(data_list)
    
    for item in tests.missing_attributes_items:
        assert item.blah=="hoho", "values should be still set"
        assert hasattr(item, 'bluh') and item.bluh == None,\
                "allow_missing_attributes should set the attributes to none unless specified"
    
def test_allow_missing_with_false_set_attribute():
    """Test a packet encoder with some missing attributes and allow_missing_attributes
    and set_missing_attributes to False."""
    test_file = "allow_missing_attributes_notset.xml"
    
    data_list = [DummyObject(titi=i, toto=i*2, blah="hoho") for i in range(100)]

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    
    error_happened = False
    try:
        output_files = manager.process("main", params=dict(data=data_list))
    except AttributeError:
        error_happened = True
        
    assert error_happened is False, "An AttributeError shouldn't have occured"
    
    assert len(tests.missing_attributes_items) == len(data_list)
    
    for item in tests.missing_attributes_items:
        assert item.blah=="hoho", "values should be still set"
        assert not hasattr(item, 'bluh'),\
                "allow_missing_attributes shouldn't set the attributes to none here"
    

#    assert len(tests.reordering_vals) == len(data_list)
#    
#    assert tests.reordering_vals != data_list
#    
#    assert tests.reordering_vals == list(sorted(data_list,
#                                                key=attrgetter('reorder_val')))
    