import collections
import itertools
import operator
import tempfile
import os

from pyf.dataflow.core import component, BYPASS_VALS
from pyf.componentized.components.writer import BaseFileWriter
from pyf.componentized.configuration.keys import SimpleKey

def buftee(iterable, n=2):
    """ An itertools.tee clone that also returns the internal buffers """
    it = iter(iterable)

    deques = [collections.deque() for i in range(n)]

    def gen(mydeque):
        next = it.next
        while True:
            if not mydeque:             # when the local deque is empty
                newval = next()       # fetch a new value and
                for d in deques:        # load it to all the deques
                    d.append(newval)
            yield mydeque.popleft()

    return tuple([(gen(d), d) for d in deques])

class MultipleFileWriter(BaseFileWriter):
    configuration = [SimpleKey('splitkey',
                               label="Split Attribute (optionnal)",
                               help_text="Attribute with which to split files"),]
    outputs_files = True
    
    def __init__(self, config_node, name):
        self.name = name
        self.config_node = config_node
        self.key_getter = None
        
    def initialize(self):
        self.key_getter_node = self.get_config_key_node('splitkey')
        if self.key_getter_node is not None and self.key_getter_node.text is not None:
            key_type = self.key_getter_node.get('type', 'attribute')
            key_content = self.key_getter_node.text.strip()
            
            self.key_getter = self.get_key_getter(key_type, key_content)
            
        else:
            self.key_getter = lambda i: None
        
        self.mapped_keys = list()
        self.iterators = list()
            
    def get_key_getter(self, key_type, content):
        if key_type == "attribute":
            return operator.attrgetter(content)
        elif key_type == "item":
            return operator.itemgetter(content)
        elif key_type == "code":
            code_item = compile(content, '<code>', 'eval')
            
            return lambda item, code_item=code_item: eval(code_item)
        else:
            raise ValueError, "Key type %s not supported" % key_type
        
    def filter_values(self, values, key):
        for value in values:
            if self.key_getter(value) == key:
                yield value
            else:
                yield Ellipsis

    def init_filename(self, key, sample_item=None):
        output_filename = self.prepare_filename(self.get_config_key('target_filename'),
                                                sample_item=sample_item,
                                                key=key)
        filename = self.get_output_filename(output_filename)
        return output_filename, filename
    
    def main_flow_wrapper(self, values):
        while True:
            try:
                item = values.next()
                key_result = self.key_getter(item)
                
                if key_result not in self.mapped_keys:
                    (values, myqueue), (other_values, otherqueue) = buftee(values, 2)
                    other_values = itertools.chain([item], other_values)
                    
                    other_values = self.filter_values(other_values,
                                                      key_result)
                    
                    self.add_key_writer(key_result,
                                        other_values,
                                        otherqueue,
                                        sample_item=item)
                    
                yield True
                
            except StopIteration:
                break
            
    def add_key_writer(self, key, flow, tee_buffer, sample_item=None):
        input_buffer = collections.deque()
        
        in_flow = self.prepare_input_flow(flow, input_buffer)
        
        kvalue = key
        if not isinstance(kvalue, basestring):
            kvalue = repr(kvalue)
            
        output_filename, temp_filename = self.init_filename(kvalue,
                                                            sample_item=sample_item)
        
        iterator = self.write(in_flow,
                              key,
                              temp_filename,
                              output_filename)
        
        out_iterator = self.prepare_output_flow(iterator,
                                               input_buffer,
                                               flow.next)
        
        self.iterators.append((out_iterator,
                               input_buffer,
                               tee_buffer))
        
        self.mapped_keys.append(key)
    
    def prepare_input_flow(self, flow, inbuffer):
        while True:
            # hangs on stopiteration
            if inbuffer:
                value = inbuffer.popleft()
            else:
                value = flow.next()

            if value in BYPASS_VALS:
                # bypass_buffer.append(value)
                # TODO: if needed, implement other direction buffer (from in to
                # out)
                pass
            else:
                yield value

    def prepare_output_flow(self, flow, input_buffer, nexter):
        while True:
            # In case we got more output value than input :)
            while input_buffer:
                yield flow.next()

            try:
                up_val = nexter()
            except StopIteration:
                # in case our main down flow is finished,
                # raises stopiteration too, which isn't catched.
                yield flow.next()
                continue

            if up_val in BYPASS_VALS:
                yield up_val
            else:
                input_buffer.append(up_val)
                # will stop on stopiteration...
                yield flow.next()

    @component('IN', 'OUT')
    def launch(self, values, out):
        self.initialize()

        self.in_count = 0
        def increment_input_count(val):
            for v in val:
                self.in_count += 1
                yield v
                
        values = increment_input_count(values)
        
        self.iterators.append((self.main_flow_wrapper(values), None, None))
        self.burnt_sources = list()
        
        while True:
            for i in range(len(self.iterators)):
                (iterator, input_buffer, tee_buffer) = self.iterators[i]

                if not iterator in self.burnt_sources:
                    val = None
                    try:
                        while tee_buffer:
                            val = iterator.next()
                            if not val:
                                yield val

                        val = iterator.next()
                        if not val:
                            yield val
                            
                    except StopIteration:
                        self.burnt_sources.append(iterator)
                        continue
                else:
                    # In case we didn't iterate on the flow in the template
                    if tee_buffer:
                        tee_buffer.clear()

            for fill in range(self.in_count):
                yield True

            self.in_count = 0

            if len(self.burnt_sources) >= len(self.iterators):
                break
        
    def write(self, values, key, output_file, target_filename):
        raise NotImplemented, "You shouldn't call the multi writer directly, "\
                             +"but use a plugin that is based on it."

