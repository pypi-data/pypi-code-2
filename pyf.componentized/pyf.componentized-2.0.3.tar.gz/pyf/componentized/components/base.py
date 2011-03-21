import compiler
from pyf.dataflow import component
from pyf.componentized.components.configuration import Configuration
from pyf.componentized import ET

import logging
import operator
from pyf.componentized.configuration.keys import SimpleKey, ComplexCompoundKey,\
    BooleanKey
log = logging.getLogger(__name__)

def indent(input, level=0, level_num=4):
    new_output = ""
    for line in input.split('\n'):
        new_output += (" " * level * level_num) + line + '\n'
    return new_output    

class ComponentMetaClass(type): 
    def __new__(metaclass, classname, bases, class_dict): #@NoSelf, this is a metaclass
        def document_key(key, level):
            v = '- %s: %s' % (key['label'] and '"**%s**" `(label: %s)`' % (key['key'], key['label'])
                                               or '"**%s**" `(label: %s)`' % (key['key'], key['key'].title()),
                                  key['type_info'])
            if key.get('default'):
                v += ' (default: "%s")' % key['default']
            
            v += "\n"
            
            if key.get('help_text'):
                v += '    %s\n' % key['help_text']
                
            if key.get('sub_keys'):
                v += document_subkeys(key.get('sub_keys'), level = level + 1)
                
            if key.get('content'):
                if key.get('content_title'):
                    v+= '    %s\n' % key.get('content_title')
                    
                v += document_subkeys([key.get('content')], level = level + 1)
                
            return v
        
        def document_subkeys(configuration_keys, level=2):
            val = ""
            for key in configuration_keys:
                val += document_key(key, level)
                
            return indent(val, level=level)
        
        def document_keys(configuration_keys, level=2):
            val = ""
            for key in configuration_keys:
                val += document_key(key.document(), level)
                
            return indent(val, level=level)
        
        get_bases = operator.attrgetter('__bases__')
        get_recursive_bases = lambda dd: reduce(operator.add,
                                                [get_bases(cd)
                                                 and [cd] + get_recursive_bases(
                                                                    get_bases(cd))
                                                 or [cd, ]
                                                 for cd in dd])
        
        base_list = reversed(get_recursive_bases(bases))
        configuration_list = list()
        for base_name, base in [(b.__name__, b.__dict__)
                                for b in base_list] + [(classname,class_dict)]:
            if base.get('configuration'):
                for key in base.get('configuration'):
                    if key.key in map(operator.attrgetter('key'),
                                      configuration_list):
                        configuration_list.remove(filter(lambda x: x.key == key.key,
                                                         configuration_list)[0])
                    
                    configuration_list.append(key)
        
        class_dict['configuration'] = configuration_list or None
        
        if len(configuration_list) > 0:
            new_doc = class_dict.get('__doc__', "") + "\n\n    **Configuration available :**\n"
            new_doc += document_keys(configuration_list)
            class_dict['__doc__'] = new_doc
            
        return type.__new__(metaclass, classname, bases, class_dict)
    


class Component(object):
    
    __metaclass__ = ComponentMetaClass
    
    configuration = [ComplexCompoundKey('advanced',
                                        content=[BooleanKey('separate_process',
                                                            label="Separate Process")],
                                        collapsible=True,
                                        collapsed=True,
                                        label='Advanced'),
                    SimpleKey('name', help_text="unique name")]
    
    @property
    def has_configuration_protocol(self):
        return hasattr(self, 'configuration') and self.configuration is not None
    
    @property
    def configuration_keys(self):
        if self.has_configuration_protocol:
            return dict([(ckey.key, ckey) for ckey in self.configuration])
        else:
            return None
    
    def get_config_key(self, key, default=None):
        """ Returns a config key for the current process and id
            or default value.
            If the configuration protocol is defined, it will return a fully formatted value.
            Else, it will return the node content text. """
        node = self.get_config_key_node(key)
        if node is None:
            return default
        
        if self.has_configuration_protocol and self.configuration_keys.get(key):
            if hasattr(self.configuration_keys.get(key), 'gets_node_list')\
               and self.configuration_keys.get(key).gets_node_list:
                return self.configuration_keys[key].from_xml(self.get_config_key_nodes(key),
                                                             default=default)
            else:
                return self.configuration_keys[key].from_xml(node, default=default)
        else:
            return self.__simple_get_config_key(key, default=default)
    
    def __simple_get_config_key(self, key, default=None):
        """ Returns a config key for the current process and id
            or default value """
        val = self.__simple_get_config_key_in_node(self.config_node, key)
        if val is None and hasattr(self, 'process_config_node'):
            val = self.__simple_get_config_key_in_node(self.process_config_node, key)
        
        if val is not None:
            return val
        else:
            return default
        
    def __simple_get_config_key_in_node(self, node, key, default=None):
        """ Returns a config key searching in a specific node """
        key_node = node.find(key)
        if key_node is not None:
            if key_node.text is not None and key_node.text != "":
                return key_node.text
            else:
                return default
        else:
            return default
        
    def get_config_key_node(self, key):
        node_current = self.config_node.find(key) # local config
        if node_current is None and hasattr(self, 'process_config_node'):
            node_current = self.process_config_node.find(key) # global config
        
        return node_current

    def get_config_key_nodes(self, key):
        # first look at local config
        nodes_current = self.config_node.findall(key)

        if (nodes_current is None or len(nodes_current) == 0) \
                and hasattr(self, 'process_config_node'):
            # found nothing in local config, let's look at global config
            nodes_current = self.process_config_node.findall(key)

        return nodes_current

    def set_config_key(self, key, value):
        """ Sets a config key for the current process and id.
            WARNING: Dangerous, shouldn't be used. """
        key_node = self.config_node.find(key)
        if key_node is None:
            key_node = ET.SubElement(self.config_node, key) #@UndefinedVariable
            
        key_node.text = value
        
    def set_process_config_node(self, node):
        self.process_config_node = node
        
    def set_output_file_getter(self, getter):
        self.registered_output_files = list()
        self._get_output_file = getter
        
    def get_output_filename(self, target_filename):
        if not hasattr(self, '_get_output_file'):
            raise ValueError("Please don't try to get an output file before run.")
        
        # TODO: implement replace
        
        temp_filename = self._get_output_file(target_filename)
        self.registered_output_files.append((temp_filename, target_filename))
        
        return temp_filename
        
    @property
    def params(self):
        if hasattr(self, '_params'):
            return self._params
        else:
            return None
    
    @property
    def message_callback(self):
        return self._get_message_callback()
        
    def _get_message_callback(self):
        if hasattr(self, '_message_callback'):
            return self._message_callback
        else:
            return log.info
        
    def set_params(self, params):
        self._params = params
        
    def set_message_callback(self, message_callback):
        self._message_callback = message_callback
    
    def get_configuration(self):
        config_node = 'configuration'
        config = Configuration()

        if hasattr(self, 'process_config_node'):
            configuration_node = self.process_config_node.find('config')
            if not configuration_node is None:
                config.read(configuration_node)

            configuration_node = self.process_config_node.find(config_node)
            if not configuration_node is None:
                config.read(configuration_node)

        configuration_node = self.config_node.find(config_node)
        if not configuration_node is None:
            config.read_xml_node(configuration_node)

        return config
        
class CodeComponent(Component):
    """ When you create a node from code (not from plugin: code adapters, code producers, code consumers),
    a CodeComponent is instanced.
    
    There is three types of code blocks :
      - `function` (default value, and forced for producers):
          Your code is executed and imported like an external module.
          
          Instructions for your code :
              The **last function** of your code is called.
              
              Your function should have:
                - no argument if it's a producer,
                - an iterator as argument if it's an adapter or a consumer.
              
              You function should be a **generator**, **yielding items or statuses** (True if ok / False if error)
              if it's a consumer.
              
              Variables magically accessible:
                  - `message_callback` (function): a function taking a message as an unicode string, that will
                    be passed to the message dispatching system (ex. in pyf.services it will be shown in the event track).
                  - `progression_callback` (function, only for producers): a function taking an integer or a decimal.Decimal
                    that will update the progress of the process.
                  - `get_config_key` (function): gets the value of the configuration node specified as first argument (second argument is the default value).
                    
      - `exec`:
          Your code is executed before yielding the item.
          You can modify the "item" variable as you like (usefull for adapters).
          Accessible variable :
            - `item`: the item entering your adapter.
            
      - `eval` (only for adapters):
          Will yield the result of the eval.
          Accessible variable :
            - `item`: the item entering your adapter.
    """
    def __init__(self, config_node, name, gets_data=True):
        super(CodeComponent, self).__init__()
        
        self.config_node = config_node
        self.name = name
        
        self.code_node = self.config_node.find('code')
        self.code_text = self.code_node.text.strip()
        
        if gets_data:
            self.code_type = self.code_node.get('type', 'function')
            if self.code_type == 'function':
                self.introspect_function()
                self.code = compile(self.code_text, '<component "%s">' % self.name, 'exec')
                self.launch = self.launch_function
                
            elif self.code_type == 'exec':
                self.code = compile(self.code_text, '<component "%s">' % self.name, 'exec')
                self.launch = self.launch_exec
                
            elif self.code_type == 'eval':
                self.code = compile(self.code_text, '<component "%s">' % self.name, 'eval')
                self.launch = self.launch_eval
        else:
            self.introspect_function()
            self.code = compile(self.code_text, '<component "%s">' % self.name, 'exec')
            self.launch = self.launch_producer
        
    def introspect_function(self):
        """
        Gets the name of the last element of the code block.
        This is used to get the name of the function to execute.
        """
        self.code_func_name = compiler.parse(self.code_text,
                                             'exec').node.nodes[-1].name
                                             
    @component('IN', 'OUT')
    def launch_function(self, values, out):
        evaldict = dict(out=out,
                        get_config_key=self.get_config_key,
                        get_config_key_node=self.get_config_key_node,
                        get_config_key_nodes=self.get_config_key_nodes,
                        config_node=self.config_node,
                        message_callback=self.message_callback,
                        param=self.params)
        exec self.code in evaldict
        for result in evaldict[self.code_func_name](values):
            yield result
            
    @component('IN', 'OUT')
    def launch_exec(self, values, out):
        for item in values:
            exec self.code
            yield item
    
    @component('IN', 'OUT')
    def launch_eval(self, values, out):
        for item in values:
            yield eval(self.code)
            
    def launch_producer(self, progression_callback=None,
                        message_callback=None, params=None):
        evaldict = dict(progression_callback=progression_callback,
                        message_callback=message_callback,
                        params=params,
                        get_config_key=self.get_config_key,
                        get_config_key_nodes=self.get_config_key_nodes,
                        get_config_key_node=self.get_config_key_node)
        exec self.code in evaldict
        return evaldict[self.code_func_name]()
