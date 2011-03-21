from pyf.componentized.core import Manager
from pyf.componentized import ET
from pyf.transport import Packet

import os
import random
from operator import attrgetter


# dummy data holder
from pyf.components.adapters.reordering import tests

DATADIR = "pyf/components/adapters/reordering/tests/data"

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

def test_simple_object_attribute_reordering():
    """Test a simple reordering."""
    test_file = "reordering_tube.xml"
    
    data_list = [DummyObject(reorder_val=i, toto=i*2) for i in range(100)]
    random.shuffle(data_list)

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    output_files = manager.process("main", params=dict(data=data_list))
    
    assert len(tests.reordering_vals) == len(data_list)
    
    assert tests.reordering_vals != data_list
    
    assert tests.reordering_vals == list(sorted(data_list,
                                                key=attrgetter('reorder_val')))
    
def test_packet_attribute_reordering():
    """Test a simple packet reordering."""
    test_file = "reordering_tube.xml"
    
    data_list = [Packet(dict(reorder_val=i, toto=i*2)) for i in range(100)]
    random.shuffle(data_list)

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    output_files = manager.process("main", params=dict(data=data_list))
    
    assert len(tests.reordering_vals) == len(data_list)
    
    assert tests.reordering_vals != data_list
    
    assert map(repr, tests.reordering_vals)\
             == map(repr,
                    sorted(data_list,
                           key=attrgetter('reorder_val')))
    
def test_packet_attribute_reordering_with_packet_marshal():
    """Test a simple packet reordering with packet_parshal serializing system."""
    test_file = "reordering_tube_packet_marshal.xml"
    
    data_list = [Packet(dict(reorder_val=i, toto=i*2)) for i in range(100)]
    random.shuffle(data_list)

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    output_files = manager.process("main", params=dict(data=data_list))
    
    assert len(tests.reordering_vals) == len(data_list)
    
    assert tests.reordering_vals != data_list
    
    assert map(repr, tests.reordering_vals)\
             == map(repr,
                    sorted(data_list,
                           key=attrgetter('reorder_val')))
             
def test_simple_object_eval_reordering():
    """Test a simple reordering with eval key."""
    test_file = "reordering_tube_eval.xml"
    
    data_list = [DummyObject(reorder_val=i, toto=i*2) for i in range(100)]
    random.shuffle(data_list)

    network_file = open(os.path.join(DATADIR, test_file), 'r')
    network_xml = network_file.read()
    network_file.close()

    manager = Manager(ET.fromstring(network_xml))
    output_files = manager.process("main", params=dict(data=data_list))
    
    assert len(tests.reordering_vals) == len(data_list)
    
    assert tests.reordering_vals != data_list
    
    assert tests.reordering_vals == list(sorted(data_list,
                                                key=lambda v: v.reorder_val*-1))