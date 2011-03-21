from pyf.componentized.components.adapter import BaseAdapter
from pyf.componentized.configuration.keys import RepeatedKey, CompoundKey,\
    BooleanKey, SimpleKey
from pyf.componentized.configuration.fields import InputField, SingleSelectField
from pyjon.utils import create_function
import operator
import decimal
from pyf.transport import Packet
from pyf.dataflow.core import component
from pyf.components.adapters.standardtools.adapter import DynamicObjectAdapter

class Summarizer(BaseAdapter):
    name = "summarizer"
    
    configuration = [RepeatedKey('summaries', 'summary',
                                 content=CompoundKey('summary',
                                                     text_value='getter',
                                                     attributes={'name': 'name',
                                                                 'getter_type': 'getter_type',
                                                                 'summary_type': 'summary_type'},
                                                     fields=[InputField('name', label="Attribute",
                                                                        help_text="Target attribute"),
                                                             SingleSelectField('summary_type',
                                                                               label='Summary Type',
                                                                               default='sum',
                                                                               values=['sum',
                                                                                       'average',
                                                                                       'unique_values']),
                                                             SingleSelectField('getter_type',
                                                                               label='Data Getter',
                                                                               default='eval',
                                                                               values=['eval',
                                                                                       'attribute',
                                                                                       'item']),
                                                             InputField('getter', label="Getter",
                                                                        help_text='Value to get. (ex. "item.test" or "test", depending on type)')])),
                     BooleanKey('yield_items',
                                label="Yield Items (or just the summary at the end)",
                                default=False),
                     SimpleKey('summary_attribute',
                               label="Attribute of summary",
                               help_text="optional, only active if set",
                               default="")]
    
    _design_metadata_ = dict(default_width=295)
    
    def __init__(self, config_node, name):
        super(Summarizer, self).__init__(config_node, name)

        self.summaries = dict()
            
    def compile_summaries(self):
        for summary in self.get_config_key('summaries'):
            summary_name = summary.get('name')
            getter_text = summary.get('getter').strip()
            getter_type = summary.get('getter_type') or 'attribute'
            summary_type = summary.get('summary_type') or 'sum'

            if getter_type == 'eval':
                getter_code = compile(getter_text, '<component "%s">' % self.name, 'eval')
                
                def getter(item, getter_code, name):
                    get_config_key = self.get_config_key
                    get_config_key_node = self.get_config_key_node

                    try:
                        return eval(getter_code)
                    except Exception, e:
                        self.message_callback("Error on summarized attribute %s of %s: %s"\
                                              % (name,
                                                 self.name,
                                                 str(e)), message_type="error")
                        raise
                
                getter_func = create_function(getter,
                                              args=[getter_code,
                                                    summary_name],
                                              caller_args_count=1)
            
            elif getter_type == 'attribute':
                getter_func = operator.attrgetter(getter_text)
            
            elif getter_type == 'item':
                getter_func = operator.itemgetter(getter_text)
            
            if summary_type == 'sum':
                summary_func = operator.add
                
            elif summary_type == 'unique_values':
                def summary_func(a,b):
                    if not isinstance(a, set):
                        a = set([a])
                    a.add(b)
                    return a
                
            elif summary_type == 'average':
                def average_factory():
                    """ Warning, it's a reduce-like function for average factory.
                    Don't reuse a function generated like this is another reduce.
                    """
                    current_set = list()
                    
                    def func(a, b):
                        if not current_set:
                            current_set.append(1)
                            current_set.append(a)
                        
                        if isinstance(current_set[1], int):
                            current_set[1] = float(current_set[1])
                            
                        current_set[0] = current_set[0] + 1
                        current_set[1] = current_set[1] + b
                        
                        return current_set[1] / current_set[0]
                    
                    return func
                
                summary_func = average_factory()
                
            self.summaries[summary_name] = dict(name=summary_name,
                                                getter=getter_func,
                                                summarizer=summary_func)
    
    @component('IN', 'OUT')
    def launch(self, values, out):
        self.compile_summaries()
        
        summary_list = [(summary['name'],
                         summary['getter'],
                         summary['summarizer'])
                        for summary in self.summaries.values()]
        
        yield_items = self.get_config_key('yield_items', False)
        summary_attribute = self.get_config_key('summary_attribute', None)
        apply_attribute = bool(summary_attribute)
        
        current_values = Packet()
        for i, value in enumerate(values):
            if i == 0:
                for name, getter, summarizer in summary_list:
                    current_values[name] = getter(value)
                    
            else:
                for name, getter, summarizer in summary_list:
                    current_values[name] = summarizer(current_values[name],
                                                      getter(value))
            
            if yield_items and apply_attribute:
                value = DynamicObjectAdapter(value)
                value.add_attribute_value(apply_attribute, current_values)
                
            elif yield_items and not apply_attribute:
                yield (out, value)
                
            else:
                yield (out, Ellipsis)
        
        if not (apply_attribute and yield_items):
            # we yield the summary object only if we didn't pass it with the items
            yield current_values