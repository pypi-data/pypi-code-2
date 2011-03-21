import datetime
import decimal

import compiler

from pyf.dataflow import component

from pyjon.utils.main import create_function

from pyf.componentized.components import BaseAdapter
from pyf.componentized.configuration.keys import RepeatedKey, CompoundKey,\
    SimpleKey
from pyf.componentized.configuration.fields import InputField, SingleSelectField
from pyf.transport.packets import Packet

class ComputeAttributes(BaseAdapter):
    name = "compute_attributes"
    
    configuration = [RepeatedKey('attributes', 'attribute',
                                 content=CompoundKey('attribute',
                                                     text_value='getter',
                                                     attributes={'name': 'name',
                                                                 'type': 'type'},
                                                     fields=[InputField('name', label="Attribute",
                                                                        help_text="Target attribute"),
                                                             SingleSelectField('type',
                                                                               label='Type',
                                                                               default='eval',
                                                                               values=['eval',
                                                                                       'function']),
                                                             InputField('getter', label="Value",
                                                                        help_text='Value to apply. (ex. "base_item.test")')]))]
    
    _design_metadata_ = dict(default_width=295)
    
    def __init__(self, config_node, name):
        super(ComputeAttributes, self).__init__(config_node, name)

        self.getters = dict()

        self.compile_getters()
            
    def compile_getters(self):
        for attribute in self.get_config_key('attributes'):
            getter_name = attribute.get('name')
            getter_text = attribute.get('getter').strip()
            getter_type = attribute.get('type') or 'eval'

            if getter_type == 'eval':
                getter_code = compile(getter_text, '<component "%s">' % self.name, 'eval')
                
                def getter(item, base_item, getter_code, name):
                    get_config_key = self.get_config_key
                    get_config_key_node = self.get_config_key_node

                    try:
                        return eval(getter_code)
                    except Exception, e:
                        self.message_callback("Error on attribute %s of %s: %s"\
                                              % (name,
                                                 self.name,
                                                 str(e)), message_type="error")
                        raise
                
                self.getters[getter_name] = create_function(getter,
                                                            args=[getter_code,
                                                                  getter_name],
                                                            caller_args_count=2)
            
            elif getter_type == 'function':
                getter_func_name = compiler.parse(getter_text,
                                                  'exec').node.nodes[-1].name
                getter_code = compile(getter_text, '<component "%s">' % self.name, 'exec')
                
                def getter(item, base_item, getter_code, getter_func_name, name):
                    evaldict = dict(item=item,
                                    base_item=base_item,
                                    decimal=decimal,
                                    datetime=datetime,
                                    get_config_key=self.get_config_key,
                                    get_config_key_node=self.get_config_key_node)
                    try:
                        exec getter_code in evaldict
                        return evaldict[getter_func_name]()
                    
                    except Exception, e:
                        self.message_callback("Error on attribute %s of %s: %s"\
                                              % (name,
                                                 self.name,
                                                 str(e)), message_type="error")
                        raise e
                
                self.getters[getter_name] = create_function(getter,
                                                            args=[
                                                              getter_code,
                                                              getter_func_name,
                                                              getter_name],
                                                            caller_args_count=2)
    
    @component('IN', 'OUT')
    def launch(self, values, out):
        for value in values:
            value = DynamicObjectAdapter(value)
            
            for key, getter in self.getters.iteritems():
                value.add_attribute_getter(key, getter)
            
            yield (out, value)
            
class SetAttributes(BaseAdapter):
    name = "set_attributes"
    
    configuration = [RepeatedKey('attributes', 'attribute',
                                 content=CompoundKey('attribute',
                                                     text_value='value',
                                                     attributes={'name': 'name'},
                                                     fields=[InputField('name', label="Attribute",
                                                                        help_text="Target attribute"),
                                                             InputField('value', label="Value",
                                                                        help_text='Static value (ex. "foo")')]))]
    
    def __init__(self, config_node, name):
        super(SetAttributes, self).__init__(config_node, name)
        
        attributes = self.get_config_key('attributes')
        
        self.values = dict()
        for value_node in attributes:
            value_name = value_node.get('name')
            value = value_node.get('value')
            self.values[value_name] = value
    
    @component('IN', 'OUT')
    def launch(self, values, out):
        for value in values:
            value = DynamicObjectAdapter(value)
            
            for key, val in self.values.iteritems():
                value.add_attribute_value(key, value)
            
            yield (out, value)
            
class SAObjectScrubber(BaseAdapter):
    name = "sa_object_scrubber"
    
    @component('IN', 'OUT')
    def launch(self, values, out):
        for value in values:
            if not isinstance(value, DynamicObjectAdapter):
                value = DynamicObjectAdapter(value)
                
            value.scrub_object()
            
            yield (out, value)
            
class SimpleFilter(BaseAdapter):
    name = "simple_filter"
    
    configuration = [SimpleKey('expression',
                               label="Filter expression",
                               help_text="filter to apply, ex: item.foo == 'bar'")]
    
    def __init__(self, config_node, name):
        super(SimpleFilter, self).__init__(config_node, name)
        
        self.filter_code = self.get_config_key('expression', "True")
        
        self.filter_code = compile(self.filter_code, '<string>', 'eval')
    
    @component('IN', 'OUT')
    def launch(self, values, out):
        for it, value in enumerate(values):
            get_config_key = self.get_config_key
            item = base_item = value
            
            if eval(self.filter_code):
                yield (out, value)
            else:
                yield (out, Ellipsis)

class dummyobj(object):
    pass

def scrub_sa_object(item, **kwargs):
    """this is a small helper function that transforms an SQLAlchemy object
    into a bare simple object.
    This bare object will just contain the attributes related to the columns
    that were declared in the SA model. This permits to use this object in
    serialisers that would not know how to handle the whole SA attributes.
    """
    new_item = dummyobj()
    
    for attribute in item._sa_class_manager.mapper.c:
        key = attribute.key
        setattr(new_item, key, getattr(item, key))

    for key, value in kwargs.items():
        setattr(new_item, key, value)
    
    return new_item
    
            
class DynamicObjectAdapter(object):
    def __init__(self, former_object):
        self.former_object = former_object
        self.scrubbed = False
        self.__attributes = dict()
        self.__attribute_getters = dict()
        
        self.__initialized = True
        
    def add_attribute_getter(self, key, getter):
        self.__attribute_getters[key] = getter
        
    def add_attribute_value(self, key, value):
        self.__attributes[key] = value
        
    def scrub_object(self, **kwargs):
        new_item = scrub_sa_object(self.former_object, **kwargs)
        
        self.scrubbed = True
        self.former_object = new_item
        
    def compute_getter(self, key):
        return self.__attribute_getters[key](self, self.former_object)
    
    def __hasattr__(self, key):
        return (key in self.__attributes
                or key in self.__attribute_getters
                or hasattr(self.former_object, key))
    
    def __getattr__(self, attribute):
        if attribute in self.__attributes:
            return self.__attributes[attribute]
        elif attribute in self.__attribute_getters:
            return self.compute_getter(attribute)
        else:
            return getattr(self.former_object, attribute)
    
    def __setattr__(self, attribute, value):
        if not self.__dict__.has_key('_DynamicObjectAdapter__initialised'):
            return object.__setattr__(self, attribute, value)
        elif self.__dict__.has_key(attribute):
            object.__setattr__(self, attribute, value)
        else:
            self.add_attribute_value(attribute, value)
    
    def serialize(self):
        obj_attrs = dict()
        if hasattr(self.former_object, 'keys') and hasattr(self.former_object, 'items'):
            obj_attrs = dict(self.former_object.values())
        else:
            obj_attrs = dict(self.former_object.__dict__.items())
        
        obj_attrs.update(self.__attributes)
        obj_attrs.update([(key, self.compute_getter(key)) for key, value in self.__attribute_getters])
        
        return Packet(obj_attrs).serialized
    
    @classmethod
    def deserialize(cls, value_dict):
        return Packet.deserialize(value_dict)