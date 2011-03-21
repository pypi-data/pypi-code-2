from pyf.dataflow.components import (zip_merging,
                                     ordered_key_merging,
                                     linear_merging, izip_longest)
from pyf.componentized.components.joiner import DataJoiner
from pyf.dataflow.core import component
from pyf.dataflow.merging import merge_iterators
from pyf.transport.packets import Packet
import operator
import itertools
import time

import logging
log = logging.getLogger()

class LinearJoiner(DataJoiner):
    """ This joiner takes items from all incoming ports, doing a cycle.
    (Ex: one item from first port, one item from second, one item from first, etc.)
    
    Optional attribute : "type", default: "longest"
    Available types :
    
    * longest: takes values from all sources, filling with an Ellipsis when a source is finished,
      and stops when there are no active sources anymore.
      
      .. code-block:: xml

            <joiner pluginname="linear" type="longest" />
            
    * simple: takes values from all sources, and stops when any of the sources is finished.
    
      .. code-block:: xml

            <joiner pluginname="linear" type="simple" />
    """
    name = "linear"
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        zipper_type = self.config_node.get('type', 'longest')
        if zipper_type == 'longest':
            zipper = lambda *items: izip_longest(fillvalue=Ellipsis, *items)
        else:
            zipper = itertools.izip
            
        for row in zipper(*sources):
            for item in row:
                yield item
                
class SequencialJoiner(DataJoiner):
    """ This joiner takes items from all the sources, but one after another :
    It consumes a source entirely, then goes to the next one.
    
    .. warning::
        If use this joiner on sources that come from a single producer,
        you may take all data into memory.
    
    You may optionaly setup the order of the sources (useful if you want to chain two separate branches of a network) :
    
    .. code-block:: xml

            <joiner pluginname="sequence">
                <source name="my_first_upper_node" priority="0" />
                <source name="my_second_upper_node" priority="1" />
            </joiner>
            
    .. note::
        Lower integer means higher priority.
    """
    name = "sequence"
    
    def __get_source_names(self):
        source_nodes = self.config_node.findall('source')

        if len(source_nodes) > 0:
            return dict(
                    [(node.get('name'), node.get('priority', 0))
                      for node in source_nodes ]
                    )

        else:
            return None

    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        sources = list(sources)
        source_names = self.__get_source_names()

        ordered_sources = list()

        if source_names is not None and ports is not None:
            for i, source in enumerate(sources):
                # sources that were not explicitly assigned a priority will have 0
                ordered_sources.append(
                        (source_names.get(ports[i], 0), source)
                        )

            ordered_sources = map(
                    operator.itemgetter(1),
                    sorted(ordered_sources, key=operator.itemgetter(0))
                    )

        else:
            ordered_sources = sources

        for source in ordered_sources:
            for item in source:
                yield item

class ZipJoiner(DataJoiner):
    """ This joiner yields dictionnary with source name as keys and items in values.
    For one value in upper sources you get one dictionnary.
    
    Optional attribute : "type", default: "longest"
    Available types :
    
    * longest: takes values from all sources, filling with None when a source is finished,
      and stops when there are no active sources anymore.
      
      .. code-block:: xml

            <joiner pluginname="zip" type="longest" />
            
    * simple: takes values from all sources, and stops when any of the sources is finished.
    
      .. code-block:: xml

            <joiner pluginname="zip" type="simple" />
    
    Example :
    
        source_1 yields 'A', 'B' and 'C' and source_2 yields 'aa' and 'bb'
        
        the joiner will yield:
            1. {'source_1': 'A', 'source_2': 'aa'}
            2. {'source_1': 'B', 'source_2': 'bb'}
            3. {'source_1': 'A', 'source_2': None} (only if type is "longest", the default)
    """
    name = "zip"
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        zipper_type = self.config_node.get('type', 'longest')
        if zipper_type == 'longest':
            zipper = izip_longest
        else:
            zipper = itertools.izip
            
        for row in zipper(*sources):
            yield dict([(ports[num], item) for num, item in enumerate(row)])
                
class OrderedKeyJoiner(DataJoiner):
    """ A joiner that synchronises the input sources and yields groups similar to the ones in the "zip" joiner.
    
    .. note::
        To synchronise data sources, it uses :mod:`pyf.dataflow.merging.merge_iterators`.
        The sources have to be ordered by this key.For example, if you set AccountCode attribute
        as key on a source, you have to do an order_by AccountCode on your extractor for this source.
        
    To synchronise items, you have to set comparison keys. Basically, the merger checks
    every items from input sources and compares the keys, if two items in source A and B have the same key,
    they are yielded together, if only one source has a value with this key, it is yielded alone (and None is set
    on values for other sources).
    
    If you don't set keys, the object themselves will be compared.
    If you set only one key, it will be used for all sources.
    
    Example with same key for all sources :
    
        .. code-block:: xml
        
            <joiner pluginname="sequence">
                <key type="attribute">AccountCode</key>
            </joiner>
            
    Example with individual keys for each source :
    
     .. code-block:: xml
        
            <joiner pluginname="sequence">
                <!-- Default type is "attribute", other supported are "item" (value[item])
                    or "code" (eval, with "item" as available variable). -->
                <key source="my_first_upper_node">AccountCode</key>
                <key source="my_second_upper_node" type="code">item.Customer.CustomerCode</key>
                <key source="my_other_source" type="item">1</key> <!-- imagine this is a tuple, it will be second item of it :) -->
            </joiner>
    """
    
    name = "orderedkey"
    
    def get_keys(self):
        if len(self.config_node.findall('key')) > 0:
            keys = [(k.text.strip(),
                     k.get('type', 'attribute'),
                     k.get('source', None))
                    for k in self.config_node.findall('key')]
            if len(keys) > 1:
                return dict([(source,
                              self.prepare_key(value, type, source))
                             for value, type, source in keys])
            else:
                return self.prepare_key(*keys[0])
        else:
            return None
    
    def prepare_key(self, value, type="attribute", source=None):
        def print_middleware(func):
            def mm(vv):
                v = func(vv)
                log.debug('source %s: %r' % ((source or '').ljust(15), v))
                return v

            return mm

        if type == "attribute":
            getter = operator.attrgetter(value)
        elif type == "item":
            getter = operator.itemgetter(value)
        elif type == "code":
            code_item = compile(value, '<code>', 'eval')
            
            getter = lambda item, code_item=code_item: eval(code_item)
        else:
            raise ValueError, "Key type %s not supported on orderedkeys joiner" % type

        if self.do_debug:
            return print_middleware(getter)
        else:
            return getter
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        sources = list(sources)

        self.do_debug = self.get_config_key('debug', 'false').lower() in ['true', 'on', 'yes']

        keys = self.get_keys()
        if isinstance(keys, dict):
            keys = [keys[port] for port in ports]
        
        merger = merge_iterators(sources, key=keys)
        
        output_type = self.config_node.get('output', 'dict')
        
        if output_type == "packet":
            for row in merger:
                yield Packet(dict([(ports[num], item)
                                   for num, item in enumerate(row)]))
        else:
            for row in merger:
                yield dict([(ports[num], item)
                            for num, item in enumerate(row)])
            
class OrderedKeyMerger(OrderedKeyJoiner):
    """ Deprecated joiner, similar as using "orderedkey" with output="packet"
    """
    name = "orderedkeymerge"
    
    def get_keys(self):
        if len(self.config_node.findall('source')) > 1:
            keys = [(k.text.strip(),
                     k.get('type', 'attribute'),
                     k.get('key'),
                     k.get('source'))
                    for k in self.config_node.findall('source')]
            return dict([(source,
                          (name,
                           self.prepare_key(value,
                                            type,
                                            source)))
                         for name, type, value, source in keys])
        else:
            raise ValueError, ("To use the ordered key object merger, "
                               "please set a key with a distinct name per input"
                               " flow")
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        flows = self.get_keys()
        for row in merge_iterators(list(sources), key=[k for n, k in flows]):
            pck = Packet()
            for colnum, col in enumerate(row):
                pck[flows[ports[colnum]][0]] = col
                
            yield pck

class NeutralJoiner(DataJoiner):
    """ Simple joiner that feeds one object only to the plugin, containing a
    packet (object and dictionnary-like object) of data sources
    iterators for manual joining.
    
    .. code-block:: xml
        
            <joiner pluginname="neutral"></joiner>
    """
    name = "neutral"
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):     
        sources = list(sources)
        yield Packet(dict([(ports[num], source)
                            for num, source
                            in enumerate(sources)]))
    