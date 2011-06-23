from pyf.dataflow.core import component
from pyf.transport.packets import Packet

from pyf.manager.network import Network
from pyf.manager import DataManager

from pyf.componentized.error import DataPathError
from pyf.componentized.components import ManagedComponent, ResourceManager
from pyf.componentized import ET

import logging
log = logging.getLogger()


class ProcessPipe(object):
    """ A single process manager, instanciating all plugins needed, parsing the configuration tree and giving a simple way to launch it.

    :param config_tree: The process configuration tree
    :type process_config: ElementTree object
    :param data_manager: The manager that will handle the network and data
    :type data_manager: :class:`pyf.manager.DataManager` instance
    """
    
    def __init__(self, config_tree, data_manager, process_name, options=None):

        self.config_tree = config_tree
        self.process_name = process_name
        self.resourcemanager = ResourceManager()
        self.data_manager = data_manager

        self.process_config_node = self.config_tree.find('config')
        if self.process_config_node is None:
            self.process_config_node = ET.SubElement(self.config_tree, 'config')

        self.initialize()

        if options is not None:
            self.__update_process_config(options)

    def initialize(self):
        """Initialize the process.

        This means:

        # setting some later-required attributes
        # parsing the tree to get the component descriptions
        """
        self.components = dict()
        self.nodes = dict()
        self.nodes_to_be_linked = list()

        for node in self.config_tree.findall('node'):
            self.parse_node(node)

    def finalize_init(self, progression_callback=None, message_callback=None,
            params=None):
        """Finalize the initialization of the process.

        At this point, what still needs doing is:

        # compiling the embedded Python code
        # loading the plugins
        # linking the orphan nodes
        # setting the network up

        :param progression_callback: A function that will be called every time there is information on the process progression (can receive integers or decimal.Decimal)
        :type progression_callback: function
        :param message_callback: A function that will be called with information on the process.
        :type message_callback: function
        :param params: Parameters to be passed to the process (available to the producers)
        :type params: dict
        """
        if progression_callback:
            self.progression_callback = progression_callback
        else:
            self.progression_callback = lambda x: log.debug('Progression : %s' % x)

        if message_callback:
            self.message_callback = message_callback
        else:
            self.message_callback = log.debug

        self.params = params

        for component in self.components.values():
            self.setup_component(component)

        self.link_orphans()

        network = Network(self.nodes)
        self.data_manager.add_network(self.process_name, network)

    def __update_process_config(self, options):
        for option, value in options.iteritems():
            # try to get the appropriate config format
            already_replaced = False

            for component in self.components.values():
                if not hasattr(component.component_class, 'configuration'):
                    continue

                if component.node_tree.find(option) is not None:
                    # this node defines the option in its local config, so it's
                    # probably not the one we want to use for the config format
                    continue

                for key in component.component_class.configuration:
                    if key.key != option:
                        continue

                    # gotcha!
                    value = key.to_xml(value)

                    # remove all present keys
                    elements = self.process_config_node.findall(option)
                    for elem in elements:
                        self.process_config_node.remove(elem)

                    # add new values
                    if isinstance(value, list):
                        for elem in value:
                            self.process_config_node.append(elem)
                    else:
                        self.process_config_node.append(value)

                    # stop searching for the option
                    already_replaced = True
                    break

                # stop iterating over components
                if already_replaced:
                    break

            else:
                # nothing found: just serialize it
                if not isinstance(value, basestring):
                    if isinstance(value, int) or isinstance(value, bool):
                        value = str(value)
                    elif isinstance(value, list):
                        value = ','.join(value)
                    else:
                        raise ValueError(
                                "Type %s not supported as an option for %s (%s)" % (
                                    type(value), option, repr(value)))

                # and replace the serialized value
                element = self.process_config_node.find(option)
                if element is None:
                    element = ET.SubElement(self.process_config_node, option)

                element.text = value

    def setup_joiner(self, node):
        if node is not None:
            plugin = ResourceManager().get_joiner(node.get('pluginname'))
            return plugin(node)
        else:
            return None

    @component('IN', 'OUTA')
    def splitter(self, source, out, size=3):
        """ Splits a data source in n sources (size kwarg). This is the default splitter if no other is specified. """
        yield (out.size(), size)
        for row in source:
            if isinstance(row, Packet):
                serialized = row.serialized
                for i in range(size):
                    yield (out(i), Packet(data=serialized,
                                          data_type="serialized"))
            else:
                for i in range(size):
                    yield (out(i), row)

    def parse_node(self, config_node, before=None):
        """Parses a specific node from ET format"""
        node_id = config_node.get('name')
        if not node_id:
            raise ValueError("Node doesn't have a name !")

        node_type = config_node.tag

        if node_type == 'link':
            if not before:
                raise ValueError("Can't add a link without a parent.")

            if node_id in self.nodes:
                self.nodes[node_id].setdefault('before', list()).append(before)
            else:
                self.nodes_to_be_linked.append((node_id, before))

        else:
            component = ManagedComponent(config_node)
            self.components[component.name] = component

            if component.children:
                for child in component.children:
                    self.parse_node(child, node_id)

    def setup_component(self, component, before=None):
        """Parses a specific node from ET format"""
        node_id = component.name

        component.init_component(self.process_config_node,
                             self.progression_callback,
                             self.message_callback,
                             self.params)

        joiner = self.setup_joiner(component.joiner_info)

        node = dict(component=component.component,
                    before=(before and [before] or list()),
                    after=list(),
                    joiner=(joiner is not None) and joiner.launch or None,
                    deffer_to_process=component.advanced_config['separate_process'] and component.cptype != "producer")
                    #splitter=self.splitter)

        if component.advanced_config['separate_process']:
            component.init_process_proxy()

        if component.children:
            for child in component.children:
                node['after'].append(child.get('name'))

        self.nodes[node_id] = node

    def link_orphans(self):
        for node_id, parent in self.nodes_to_be_linked:
            self.nodes[node_id]['before'].append(parent)
            self.nodes[parent]['after'].append(node_id)


    def process(self, finalize=False):
        """Launches process.

        :param finalize: Should the process finalize (copy output files to asked folders) or not. Default: False.
        :type finalize: bool
        """
        self.message_callback(u'Launching process %s' % self.process_name)
        self.__propagate_info()
        self.__do_process()
        self.message_callback(u'Finalizing process %s' % self.process_name)
        if not finalize:
            return self.__get_finalization_info()
        else:
            self.__do_finalize_process()

    def __do_process(self):
        log.debug('getting extractor')
        self.data_manager.setup_network(self.process_name)

        self.message_callback(u'Path setup')

        status_handler = self.data_manager.get_network(self.process_name).get_status_handler()
        self.message_callback(u'Status handler setup')

        for status in status_handler:
            if not status:
                raise DataPathError("Unknown error in data path")

    def __propagate_info(self):
        for name, component in self.components.iteritems():
            component.set_params(self.params)
            component.set_message_callback(self.message_callback)

    def __do_finalize_process(self):
        for component in self.components.values():
            component.finalize()

    def __get_finalization_info(self):
        infos = list()
        for component in self.components.values():
            info = component.get_finalization_info()
            if info:
                for inf in info:
                    infos.append(inf)

        return infos


class Manager(object):
    """ The main dataflow manager.

    It will instanciate ProcessPipe objects for each of the process defined in the configuration tree.
        
    :param config_tree: Configuration Tree
    :type config_tree: ElementTree object
    """
    def __init__(self, config_tree):
        self.config_tree = config_tree
        self.process_pipes = list()
        self.data_manager = DataManager()

    def get_process_names(self):
        return [n.get('name',
            'none') for n in self.config_tree.findall('process')]

    def get_process_config(self, name):
        """ Returns the particular named process config in the configuration """
        for process in self.config_tree.findall('process'):
            if process.get('name', 'none') == name:
                return process

        return None

    def process(self, name=None, params=None, progression_callback=None,
            message_callback=None, finalize=False, process_config=None,
            options=None):
        """
        Initializes ProcessPipes, and launches processing.
        Launches the process with the given name.
        If no name is given, it will run all the available processes in the configuration.
        
        :param name: If given, will only launch process with the given name, if not, will launch all the processes
        :type name: string or None
        :param params: Parameters to be passed to the process (available to the producers)
        :type params: dict
        :param progression_callback: A function that will be called every time there is information on the process progression (can receive integers or decimal.Decimal)
        :type progression_callback: function
        :param message_callback: A function that will be called with information on the process.
        :type message_callback: function
        :param finalize: Should the process finalize (copy output files to asked folders) or not. Default: False.
        :type finalize: bool
        :param options: Options to be applied on the process tree. It will replace specified entries in the main config node with values from the passed dictionnary (if an option hasn't been specified in a component config, it will default to the root config, and that's what you can modify at run time here).
        :type options: dict or None
        :param process_config: if specified, ignore main config tree, and process with this tree instead.
        :type process_config: ElementTree object
        """
        if not name:
            returns = list()
            for process_name in self.get_process_names():
                returned = self.process(process_name,
                             params=params,
                             progression_callback=progression_callback,
                             message_callback=message_callback,
                             finalize=finalize,
                             options=options)
                if returned: returns.append(returned)
            return returns

        else:
            if process_config is None:
                process_config = self.get_process_config(name)
                
            process_pipe = ProcessPipe(process_config,
                                       self.data_manager,
                                       name,
                                       options=options)

            process_pipe.finalize_init(params=params,
                    progression_callback=progression_callback,
                    message_callback=message_callback)

            return process_pipe.process(finalize=finalize)

    def clean(self):
        self.data_manager.clean()

