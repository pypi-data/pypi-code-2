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

class LinearJoiner(DataJoiner):
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
    name = "sequence"
    
    def __get_source_names(self):
        source_nodes = self.config_node.findall('source')

        if len(source_nodes) > 0:
            return dict(
                    [ (node.get('name'), node.get('priority', 0))
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
    name = "zip"
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        zipper_type = self.config_node.get('type', 'simple')
        if zipper_type == 'longest':
            zipper = izip_longest
        else:
            zipper = itertools.izip
            
        for row in zipper(*sources):
            yield dict([(ports[num], item) for num, item in enumerate(row)])
                
class OrderedKeyJoiner(DataJoiner):
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
        if type == "attribute":
            return operator.attrgetter(value)
        elif type == "item":
            return operator.itemgetter(value)
        elif type == "code":
            code_item = compile(value, '<code>', 'eval')
            
            return lambda item, code_item=code_item: eval(code_item)
        else:
            raise ValueError, "Key type %s not supported on orderedkeys joiner" % type
    
    @component('INA', 'OUT')
    def launch(self, sources, out, ports=None):
        sources = list(sources)
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
