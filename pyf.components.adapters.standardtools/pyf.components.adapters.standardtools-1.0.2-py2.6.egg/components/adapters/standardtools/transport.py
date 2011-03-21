from pyf.componentized.components.adapter import BaseAdapter
from pyf.dataflow import component
from pyf.transport import Packet

import decimal
import datetime
from pyf.componentized.configuration.keys import SimpleKey, RepeatedKey,\
    CompoundKey, BooleanKey
from pyf.componentized.configuration.fields import InputField


def to_bool(str_value):
    return str_value.lower() in ('y', 'yes', 'true')

class PacketEncoder(BaseAdapter):
    """
    This plugin will create packets based on objects entering it.
    You can set which attributes will be taken in the packet with
    
        .. code-block:: xml
        
            <attributes>
               <attribute>attribute1</attribute>
               <attribute>attribute2</attribute>
               <!-- ... -->
            </attributes>
    """
    
    _design_metadata_ = dict(default_width=350)
    
    display_name = "Packet Encoder"
    description = """Encodes a python object to a pyf.transport Packet.
    Only the specified attributes will be on applied on the packet."""

    name = "packet_encoder"
    
    configuration = [RepeatedKey('attributes', 'attribute',
                                 label="Attributes to insert",
                                 content=SimpleKey('attribute')),
                     BooleanKey('allow_missing_attributes',
                                label="Allow missing attributes",
                                default=False),
                     BooleanKey('set_missing_attributes',
                                label="Always set missing attributes",
                                default=True)]

    def __init__(self, config_node, name):
        super(PacketEncoder, self).__init__(config_node, name)

        attributes = self.get_config_key_node('attributes').findall('attribute')
        self.attributes = [attr_node.text.strip() for attr_node in attributes]

        self.allow_missing_attributes = \
                self.get_config_key(
                    'allow_missing_attributes', False)
                
        self.put_missing_attributes = \
                self.get_config_key(
                    'set_missing_attributes', True)

    @component('IN', 'OUT')
    def launch(self, values, out):
        if self.put_missing_attributes:
            getter = self.allow_missing_attributes and\
                 (lambda it, at: getattr(it, at, None)) or getattr
                 
            for value in values:
                yield Packet(dict([(attr, getter(value, attr))
                                     for attr in self.attributes]))
        else:
            if self.allow_missing_attributes:
                for value in values:
                    yield Packet(dict([(attr, getattr(value, attr))
                                       for attr in self.attributes
                                       if hasattr(value, attr)]))
                    
            else:
                for value in values:
                    yield Packet(dict([(attr, getattr(value, attr))
                                         for attr in self.attributes]))
                

class PacketDuplicator(BaseAdapter):
    """
    This plugin will duplicate packets entering it the number of times specified.
    Moreover, you can set attribute override for specific iterations of the
    repeats.

    For example, let's say you want to duplicate an entering packet two times
    and changing the DebitCredit attribute on it on the second packet :

        .. code-block:: xml

            <node type="adapter" pluginname="packet_duplicator" name="repeater">
                <count>2</count>
                <overrides>
                    <override iterations="2" attribute="DebitCredit">
                        (base_item.DebitCredit == "D") and "C" or "D"
                    </override>
                </overrides>
            </node>

    Please note two things:
        - the "iterations" attribute is a comma separated value, if you want to
          apply on 2, 3 and 5 just enter "2,3,5". (it starts on 1, not 0)
          It is not mandatory : if you want the override applied on all iterations, just don't specify it.
        - attribute_override are evals, you have access to base_item, item,
          Packet, decimal and datetime.
    """

    name = "packet_duplicator"
    display_name = "Packet Duplicator"
    
    configuration = [SimpleKey('count'),
                     RepeatedKey('overrides', 'override',
                                 label="Overrides",
                                 collapsible=True,
                                 content=CompoundKey('override',
                                                     text_value='getter',
                                                     attributes={'attribute': 'attribute',
                                                                 'iterations': 'iterations'},
                                                     fields=[InputField('attribute', label="Attribute",
                                                                        help_text="Target attribute"),
                                                             InputField('iterations', label="Iterations",
                                                                        help_text='Iterations to apply on. Ex: "1, 2"'),
                                                             InputField('getter', label="Value",
                                                                        help_text='Value getter (ex. "base_item.foo")')]))]
    
    _design_metadata_ = dict(default_width=350)

    def __init__(self, config_node, name):
        super(PacketDuplicator, self).__init__(config_node, name)

        self.overrides = [(override_node.get('attribute'),
                           (override_node.get('iterations', None)\
                            and map(int, map(str.strip, override_node.get('iterations').split(',')))\
                            or None),
                           compile(override_node.get('getter'),
                                   '<string>',
                                   'eval')
                          ) for override_node in self.get_config_key('overrides')]

        self.count = int(self.get_config_key('count', '2'))

    @component('IN', 'OUT')
    def launch(self, values, out):
        for base_item in values:
            for iteration in range(1, self.count + 1):
                item = Packet(data=base_item.serialized,
                              data_type="serialized")

                for attribute, iterations, override_code in self.overrides:
                    if iterations is None or iteration in iterations:
                        item[attribute] = eval(override_code)

                yield item
