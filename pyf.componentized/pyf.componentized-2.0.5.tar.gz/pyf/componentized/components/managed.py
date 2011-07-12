from pyf.componentized.components.resource import ResourceManager
from pyf.componentized.components.base import CodeComponent, Component
from pyf.componentized.components.writer import FileWriter
from pyf.dataflow.components import generator_to_component

from pyjon.utils import get_secure_filename

import os
import tempfile
import datetime
import shutil

import logging
from pyf.manager.network import subprocess_output_adapter, GeneratorAdapter
logger = logging.getLogger()

class ManagedComponent(object):
    def __init__(self, config_node):
        self.node_tree = config_node

        self.resourcemanager = ResourceManager()
        self.gets_values = False
        self.outputs_values = False
        self.gets_filename = False

        self.name = config_node.get('name')
        self.cptype = config_node.get('type')
        self.cpname = config_node.get('pluginname')
        self.source_mode = config_node.get('from', 'plugin')

        self.joiner_info = config_node.find('joiner')

        self.children = config_node.findall('children/node') + config_node.findall('children/link')

        advanced_node = config_node.find('advanced')
        self.advanced_config = dict(
                separate_process=False,
                )
        if advanced_node is not None:
            if advanced_node.find('separate_process') is not None:
                self.advanced_config['separate_process'] = advanced_node.find('separate_process').text.lower() in ['yes', 'true']

        self.component_class = None
        self.component_obj = None

        if self.cptype == "producer":
            if self.source_mode == "plugin":
                self.component_class = self.resourcemanager.get_producer(self.cpname)

            elif self.source_mode == "code":
                self.component_class = CodeComponent

            else:
                raise ValueError('Component source not handled: %s' % self.source_mode)

            self.outputs_values = True

        elif self.cptype == "adapter":
            if self.source_mode == "plugin":
                self.component_class = self.resourcemanager.get_adapter(self.cpname)

            elif self.source_mode == "code":
                self.component_class = CodeComponent

            else:
                raise ValueError('Component source not handled: %s' % self.source_mode)

            self.gets_values = True
            self.outputs_values = True

        elif self.cptype == "consumer":
            if self.source_mode == "plugin":
                self.component_class = self.resourcemanager.get_consumer(self.cpname)

            elif self.source_mode == "code":
                self.component_class = CodeComponent

            else:
                raise ValueError('Component source not handled: %s' % self.source_mode)

            self.gets_values = True
            if getattr(self.component_class, 'gets_filename', False):
                # Here for legacy writers that don't support file factories
                self.gets_filename = True

        else:
            raise ValueError('Component type not handled: %s' % self.cptype)

    def init_component(self, process_config_node,
                 progression_callback=None,
                 message_callback=None, params=None):

        self.process_config_node = process_config_node

        self.progression_callback = progression_callback
        self.message_callback = message_callback
        self.params = params

        self.outputs_files = getattr(self.component_class,
                                     'outputs_files', False)

        self.registered_output_files = list()
        self.use_subprocess = False

        if self.gets_values:
            if self.gets_filename:
                self.temp_filename_path = get_secure_filename()
                self.target_filename = self.get_target_filename()
                self.target_path = self.get_target_path()
                self.target_filename_path = os.path.join(self.target_path,
                                                         self.target_filename)
                
                self.component_obj = self.component_class(
                                      self.node_tree,
                                      self.name,
                                      self.temp_filename_path)
                
                self.component_obj.set_config_key('target_filename',
                                                  self.target_filename)
                self.component_obj.set_config_key('target_path',
                                                  self.target_path)
                self.component_obj.set_config_key('target_filename_path',
                                                  self.target_filename_path)
                
            else:
                self.component_obj = self.component_class(
                                      self.node_tree,
                                      self.name)
        else:
            if self.source_mode == "code":
                self.component_obj = self.component_class(
                                      self.node_tree,
                                      self.name,
                                      gets_data=False)
            else:
                self.component_obj = self.component_class(
                                      self.node_tree,
                                      self.name)
        
        if self.outputs_files and hasattr(self.component_obj,
                                          'set_output_file_getter'):
            self.component_obj.set_output_file_getter(self.register_output_file)
        
        if hasattr(self.component_obj, 'set_process_config_node'):
            if self.process_config_node is not None:
                self.component_obj.set_process_config_node(self.process_config_node)
                
    def init_process_proxy(self):
        try:
            from multiprocessing.managers import SyncManager, BaseProxy, RemoteError
            class NodeManager(SyncManager):
                pass
            
            self.manager_class = NodeManager
            self.manager_instance = self.manager_class()
            self.manager_instance.start()
#            self.use_subprocess = True
            
            self.registered_output_files = self.manager_instance.list()
            
            def function_proxy(funcname):
                def func_call(*args, **kwargs):
                    manager = NodeManager()
                    manager.start()
                    
                    rvalue = getattr(manager, funcname)(*args, **kwargs)
                    
                    try:
                        value = rvalue._getvalue()
                        
                    except RemoteError:
                        value = rvalue
                    
                    return value
                
                return func_call
            
            mapped_functions = ['_get_output_file', '_get_message_callback']
            
            for function_name in mapped_functions:
                if hasattr(self.component_obj, function_name):
                    NodeManager.register(function_name, getattr(self.component_obj,
                                                              function_name))
                    setattr(self.component_obj, function_name, function_proxy(function_name))
                
        except ImportError:
            logger.warning('No multiprocessing found')

            
    @property
    def component(self):
        if not hasattr(self.component_obj.launch, 'zf_out_ports'):
            def generator_launcher_adapter(launcher, queue, args, kwargs):
                my_generator = launcher(*args, **kwargs)
                subprocess_output_adapter(my_generator, queue)
                
#            if self.use_subprocess:
#                print "producer with subprocess"
#                import multiprocessing
#                import multiprocessing.queues
#                output_queue = multiprocessing.queues.SimpleQueue()
#                process = multiprocessing.Process(target=generator_launcher_adapter,
#                                                  args=(self.component_obj.launch,
#                                                        output_queue,
#                                                        (self.progression_callback,
#                                                         self.message_callback),
#                                                        dict(params=self.params)))
#                process.start()
#                return generator_to_component(iter(GeneratorAdapter(output_queue)))
#            
#            else:
            return generator_to_component(
                        self.component_obj.launch(
                            self.progression_callback,
                            self.message_callback,
                            params=self.params))
        
        return self.component_obj.launch
    
    @property
    def launch(self):
        return self.component_obj.launch
    
    def finalize(self):
        if self.gets_filename:
            self.target_filename_path = self.get_target_filename_path(
                                                    self.node_tree)
            self.move_file(self.temp_filename_path, self.target_filename_path)
        elif self.outputs_files:
            for temp_filename, target_filename in self.registered_output_files:
                target_filename_path = os.path.join(self.get_target_path(),
                                                    target_filename)
                self.move_file(temp_filename, target_filename_path)
            
    def register_output_file(self, target_filename):
        output_tempfile = get_secure_filename()
        self.registered_output_files.append((output_tempfile, target_filename))
        
        return output_tempfile
            
    def get_finalization_info(self):
        if self.gets_filename:
            return [(self.temp_filename_path,
                     self.get_target_filename(self.node_tree))]
            
        elif self.outputs_files:
            return self.registered_output_files
        
    def move_file(self, temp_filename_path, target_filename_path):
        """Move the temp_filename_path on target_filename_path
        """
        shutil.move(temp_filename_path, target_filename_path)

    def get_target_filename(self, config_tree=None):
        """
        """
        pattern = self.get_config_key('target_filename',
                                      '',
                                      config_tree=config_tree)
        
        target_filename = datetime.datetime.strftime(datetime.datetime.now(),
                                                     pattern)
        
        return target_filename
    
    def get_target_path(self):
        target_dir = self.get_config_key('target_directory', '')
        return target_dir
    
    def get_target_filename_path(self):
        target_filename = self.get_target_filename()
        target_dir = self.get_target_path()
        target_filename_path = os.path.join(target_dir, target_filename)
        
        return target_filename_path
    
    def get_config_key(self, key, default=None, config_tree=None):
        config_tree = config_tree or self.node_tree
        key_element = config_tree.find(key)
        if key_element is not None:
            return key_element.text.strip() or default
        else:
            return default
        
    def set_params(self, params):
        if hasattr(self.component_obj, 'set_params'):
            self.component_obj.set_params(params)
            
    def set_message_callback(self, message_callback):
        if hasattr(self.component_obj, 'set_message_callback'):
            self.component_obj.set_message_callback(message_callback)
