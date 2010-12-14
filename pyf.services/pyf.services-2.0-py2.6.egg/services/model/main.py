'''
The main model of FlowPy.
A route is basically a componentised pyf (pyf.componentized) config tree.
'''

from pyf.services.model import DeclarativeBase, DBSession
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, TEXT, String, Boolean
from sqlalchemy.orm import relation

from pyf.componentized.core import Manager as ComponentManager

from pyf.componentized import ET

import sys, StringIO
from xml.dom import minidom

import operator
from operator import itemgetter, attrgetter
import logging

import random
import datetime

def session_commit(session):
    """Commit the session
    """
    import transaction
    from zope.sqlalchemy.datamanager import join_transaction
    if not transaction.get():
        transaction.begin()
        join_transaction(session())

    t = transaction.get()
    join_transaction(session())
    t.commit()

    transaction.begin()
    join_transaction(session())


class Dispatch(DeclarativeBase):
    """ A dispatch is an item that defines a tube and a descriptor used to read
    input from a defined source.
    Sources (clients) should have a foreign key to dispatch.
    """
    __tablename__ = "dispatchs"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), unique=True, nullable=False)
    display_name = Column(Unicode(50))
    description = Column(Unicode(250))

    descriptor_id = Column(Integer, ForeignKey('descriptors.id'), nullable=True)
    descriptor = relation('Descriptor', backref='dispatchs')

    tube_id = Column(Integer, ForeignKey('tubes.id'))
    tube = relation('Tube', backref='dispatchs')

    variant_name = Column(Unicode(50), nullable=True)

    def __json__(self):
        props = dict()

        for attribute in self._sa_class_manager.mapper.c:
            key = attribute.key
            props[key] = getattr(self, key)

        return props

    def process_file(self, file_object,
                     variant=None,
                     progression_callback=None,
                     message_callback=None,
                     encoding=None,
                     options=None):
        variant_name = None
        if variant is not None:
            variant_name = variant

        return self.tube.flow(
                    variant=variant_name,
                    progression_callback=progression_callback,
                    message_callback=message_callback,
                    source=file_object,
                    descriptor=self.descriptor.get_descriptor_object(
                                                            encoding=encoding),
                    options=options)

class Tube(DeclarativeBase):
    """ A tube is an item containing a pyf.componentized configuration used to process
    a flow.

    The flow can either come from a pyf.componentized extractor or from a source and
    descriptor to read the source.

    Set the needs_source to flag a tube needing a source (file like or flow).
    Set the needs_descriptor to flag a tube needing a descripted input.
    """
    __tablename__ = "tubes"
    id = Column(Integer, primary_key=True)
    """ Numerical unique identifier of the tube (primary key) """

    name = Column(Unicode(50), unique=True, nullable=False)
    """ Unique identifier of the tube, used for simple retrieval """

    display_name = Column(Unicode(50))
    """ Display name of the tube (50 chars. max) """

    description = Column(Unicode(250))
    """ Description of the tube (250 chars. max) """

    active = Column(Boolean, nullable=False, default=True)
    """ Boolean column, flags the tube as active """

    needs_source = Column(Boolean, nullable=False, default=True)
    """ Boolean column, flags the tube as needing a source (either to be
    included in another tube, or to be launched with a dispatch and a descriptor) """

    last_run_date = Column(DateTime, nullable=True)

    payload = Column(Unicode(524288))

    def __json__(self):
        props = dict(variant_names=self.variant_names,
                     dispatchs=[dispatch.id for dispatch in self.dispatchs])

        for attribute in self._sa_class_manager.mapper.c:
            key = attribute.key
            props[key] = getattr(self, key)

        return props

    def get_config_tree(self):
        """ Return the raw ET config tree without layers or includes applied
        """
        config = ET.fromstring(self.payload)
        return config

    config_tree = property(get_config_tree, None, None)

    def get_layered_config(self, variant=None):
        """ Returns the layered ET config tree.
        Also appliees the includes before and after applying layers

        Parameters:

            variant (None, string) : the variant name to check for (optionnal). """
        config_node = self.get_config_tree()

        self.apply_includes(config_node, variant=variant)

        if variant:
            layers = DBSession.query(TubeLayer)
            layers = layers.filter(TubeLayer.tube_id == self.id)
            layers = layers.filter(TubeLayer.variant_name == variant)
            layers = layers.filter(TubeLayer.active == True)
            layers = layers.order_by(TubeLayer.priority)
            for layer in layers:
                layer.apply_on_node(config_node)
                self.apply_includes(config_node, variant=variant)

        return config_node

    def apply_includes(self, config_tree, variant=None):
        """ Applies the includes on a config_tree.
        Includes can be layered. If no variant is specified, it will use the
        passed variant as a default (typically the current run variant name).

        Parameters:
            - `variant` (None, string) : the variant name to check for (optionnal).

        Examples

            Example of simple non layered include:

            .. code-block:: xml

               <include name="foo" />

            Example of layered include (will apply layers on the included tube):

            .. code-block:: xml

               <include name="foo" layered="True" />

            Example of layered include with a variant name (will apply the variant "bar" on the included tube):

            .. code-block:: xml

               <include name="foo" layered="True" variant="bar" />

        .. note:: If there is a producer in the included tube, it will be removed and all its children will be included where the include takes place.
        """

        from pyf.services.core.modifiers import apply_modifier_set

        for parent in config_tree.getiterator():
            for node in parent:
                if node.tag == "include":
                    other_tube = Tube.by_name(node.get('name'))
                    elem_index = parent.getchildren().index(node)
                    is_layered = node.get('layered', False)
                    variant_name = node.get('variant', variant)
                    remove_producer = node.get('remove_producer',
                                               'true').lower() in ['true', 'on',
                                                                   'yes', '1']

                    if other_tube:
                        if is_layered:
                            other_conf = \
                             other_tube.get_layered_config(variant=variant_name)
                        else:
                            other_conf = \
                                     other_tube.get_layered_config(variant=None)

                        root_node = other_conf.find('process/node')
                        nodes_to_include = list()

                        if (remove_producer and
                             root_node.get('type') == "producer"):
                            nodes_to_include = \
                              root_node.findall('children/node')
                        else:
                            nodes_to_include = other_conf.findall('process/node')

                        for i, node_to_include in enumerate(nodes_to_include):
                            parent.insert(elem_index+i, node_to_include)

                        apply_modifier_set(node, parent)

                    else:
#                        raise ValueError('Tube %s not found' % node.get('name'))
                        pass

                    parent.remove(node)


    def get_post_process_config(self, variant=None):
        """ Returns the post process config if there is one or None.
        Basically a post process is defined in a <postprocess> tag, just after
        the <process name="..."> tag.

        Parameters:
            - `variant` (None, string) : the variant name to check for (optionnal).
        """
        config_node = self.get_layered_config(variant=variant)

        post_process_node = config_node.find('postprocess')

        if post_process_node is None:
            return None

        # Now, we check to see if there is node without a producer in
        # post process.
        # If there are, just enclose those nodes inside a descriptorsource
        # producer...
        first_node = post_process_node.find('node')
        if first_node.get('type') != 'producer':
            new_node = ET.Element('node', type='producer',
                                  pluginname='descriptorsource',
                                  name='postprocess_source')
            new_children = ET.SubElement(new_node, 'children')
            nodes = post_process_node.findall('node')

            # WARNING: we modify the structure on which we are iterating
            # it works because findall() returns a list x_x
            for node in nodes:
                clone_node = ET.fromstring(unicode(ET.tostring(node, encoding="utf-8"), encoding="utf-8"))
                new_children.insert(len(new_children), clone_node)
                post_process_node.remove(node)

            post_process_node.append(new_node)

        return post_process_node

    @property
    def has_postprocess(self):
        """ Boolean: The tube has a postprocess or not """
        return self.get_post_process_config() is not None

    def get_manager(self, variant=None):
        """ Returns a Componentised PyF manager for the layered config.

        Parameters
            variant (None, string) : the variant name to check for (optionnal).
        """
        config_tree = self.get_layered_config(variant=variant)

        manager = ComponentManager(config_tree)

        return manager

    def get_parameters(self):
        """ Returns the parameters for the Tube.
        Checks the <params> argument of the process and returns a dictionnary
        of the key values associated.

        Example:

            .. code-block:: xml

                <params>
                    <param>
                        <key>target_date</key>
                        <type>datetime</type>
                        <name>Target Date</name>
                        <description>End date for the extraction</description>
                        <default>10/10/1998</default>
                    </param>
                    <param>
                        <key>target_type</key>
                        <type>select</type>
                        <name>Target Type</name>
                        <default>oo</default>
                        <options>
                            <option label="toto">oo</option>
                            <option label="titi">ii</option>
                        </options>
                    </param>
                </params>

        Will translate into:

            .. code-block:: python

                {'target_date': {'key': 'target_date',
                                 'type': 'datetime',
                                 'name': 'Target Date',
                                 'description': 'End date for the extraction',
                                 'default': '10/10/1998',
                                 'order': 0},
                 'target_type': {'key': 'target_type',
                                 'type': 'select',
                                 'name': 'Target Type',
                                 'options': [{'option_label': 'toto',
                                              'option': 'oo'},
                                             {'option_label': 'titi',
                                              'option': 'ii'}],
                                 'order': 1}
                }
        """
        config_tree = self.get_config_tree()
        process_node = config_tree.find('process')
        params_node = process_node.find('params')

        if params_node is None:
            return dict()

        params = dict()

        def handle_node(cnode):
            pdict = dict()
            for node in cnode:
                if len(node) > 0:
                    pdict[node.tag] = [handle_node([sn]) for sn in node]
                else:
                    pdict[node.tag] = (node.text or '').strip()
                    for attribute in node.keys():
                        pdict['%s_%s' % (node.tag, attribute)] = \
                                                          node.get(attribute)

            return pdict

        for idx, param_node in enumerate(params_node.findall('param')):
            param_dict = dict(order=idx)
            param_dict.update(handle_node(param_node))

            if 'key' in param_dict:
                params[param_dict['key']] = param_dict

        return params

    def get_valid_options(self):
        config_tree = self.get_config_tree()
        process_node = config_tree.find('process')
        params_node = process_node.find('params')

        if params_node is not None:
            base_options = map(itemgetter('key'), self.get_parameters().values()) or list()
            valid_options_node = params_node.find('valid_options')
            other_options = valid_options_node is not None and\
                            map(str.strip, valid_options_node.text.split(',')) or list()
            return list(set(base_options + other_options))
        else:
            return list()

    @property
    def process_names(self):
        """ Returns the process names for the tube.

        .. warning:: multiple processes aren't supported yet.
        """
        return [n.get('name') for n in self.config_tree.findall('process')]

    @property
    def process_name(self):
        """ Returns the first process name of the tube
        """
        return self.process_names[0]

    def flow(self, source=None,
             variant=None,
             process_name=None,
             progression_callback=None,
             message_callback=None,
             descriptor=None,
             params=None,
             options=None):
        """ Launches the tube.

        Parameters:
            - `source` (None, generator, file) : the source of the flow, only available on descriptorsource-like producers. Shoul be a file-like object if the descriptor is set, or a generator otherwise.
            - `variant` (None, string) : the variant name to check for (optionnal).
            - `process_name` (None, string) : the process name to launch (optionnal)
            - `progression_callback` (None, function) : the callback to run on progression (optionnal)
            - `message_callback` (None, function) : the callback to run on messages (optionnal)
            - `descriptor` (None, pyjon.descriptor) : the Pyjon Descriptor to use with the file on source
            - `params` (None, dict) : the params to pass to the producer
            - `options` (None, dict) : the params to override the global config with

        Returns:
            List of finalization info for the flow...
        """

        if process_name is None:
            process_name = self.process_name

        if self.needs_source and source is None:
            raise ValueError('This tube needs a source')
        elif descriptor is not None and source is None:
            raise ValueError('You must define a file-like source if you provide'\
                             ' a descriptor')

        if params is None:
            params = dict()
        if descriptor is not None and source is not None:
            params['descriptor'] = descriptor
            params['source'] = source
        elif source is not None:
            params['data'] = source

        if not 'last_run_date' in params:
            params['last_run_date'] = self.get_last_run_date(variant=variant)

        manager = self.get_manager(variant)

        return manager.process(process_name,
                               params=params,
                               progression_callback=progression_callback,
                               message_callback=message_callback,
                               finalize=False,
                               options=options)

    def launch_post_process(self, source, variant=None,
                            progression_callback=None,
                            message_callback=None):
        """ Launches the tube post process.

        Parameters:
            - `source` (None, generator, file) : the source of the flow, should be a generator on EventTrack objects.
            - `variant` (None, string) : the variant name to check for (optionnal).
            - `progression_callback` (None, function) : the callback to run on progression (optionnal)
            - `message_callback` (None, function) : the callback to run on messages (optionnal)

        Returns:
            List of finalization info for the flow...
        """
        params = dict(data=source)
        manager = self.get_manager(variant)
        post_process_config = self.get_post_process_config(variant)

        return manager.process(self.process_name,
                               params=params,
                               progression_callback=progression_callback,
                               message_callback=message_callback,
                               finalize=True,
                               process_config = post_process_config)

    def get_ordered_layers(self, variant=None, only_active=True):
        """ Get the layer objects ordered by their priority.
        If the variant isn't specified, show all the layers """
        layers = DBSession.query(TubeLayer)
        layers = layers.filter(TubeLayer.tube_id == self.id)
        if variant:
            layers = layers.filter(TubeLayer.variant_name == variant)
        if only_active:
            layers = layers.filter(TubeLayer.active == True)

        layers = layers.order_by(TubeLayer.priority)

        return layers

    @classmethod
    def get_tubes(cls, order_by='name', **kw):
        tubes = DBSession.query(cls)
        for arg, val in kw.iteritems():
            tubes = tubes.filter(getattr(cls, arg) == val)
        tubes = tubes.order_by(order_by)
        return tubes

    @classmethod
    def by_name(cls, name):
        return DBSession.query(cls).filter(cls.name == name).first()

    def get_last_run_date(self, variant=None):
        if variant is None:
            return self.last_run_date
        else:
            variants = self.get_ordered_layers(variant=variant)
            max_date = None
            for variantobj in variants:
                if max_date is None or variantobj.last_run_date > max_date:
                    max_date = variantobj.last_run_date
            return max_date

    def get_variant_names(self, show_inactive=True):
        names = list()
        for layer in self.layers:
            if layer.variant_name not in names \
                    and (layer.active or show_inactive):
                names.append(layer.variant_name)
        return names

    @property
    def variant_names(self):
        return self.get_variant_names()

    def get_graph(self, variant=None, type="tree"):
        if type=="tree":
            return self.get_tree_graph(variant=variant)
        elif type=="network":
            return self.get_network_graph(variant=variant)

    def get_tree_graph(self, variant=None):
        config = self.get_layered_config(variant=variant)

        def get_step_info(node):
            source = node.get('from', 'plugin')
            if source == 'plugin':
                source = node.get('pluginname')

            step_dict = dict(name = node.get('name'),
                             data = dict(type=node.get('type'),
                                         plugin_name=source),
                             id=random.randint(1, 1000000),
                             children=list())
            children = node.findall('children/node')
            if children:
                for child in children:
                    step_dict['children'].append(get_step_info(child))

            return step_dict

        base_dict = get_step_info(config.find('process/node'))

        return base_dict

    def get_network_graph(self, full_tree=True,
                          variant=None, all_infos=False,
                          stripped_nodes=['children',
                                          'code',
                                          'joiner'],
                          compute_position=True):
        if full_tree:
            etree = ET
            config = self.get_layered_config(variant=variant)
        else:
            # use lxml etree to avoid loss of cdata
            from lxml import etree
            parser = etree.XMLParser(strip_cdata=False)
            config = etree.fromstring(self.payload, parser=parser)

        links = list()
        nodes = list()

        nodes_per_name = dict()

        def prettify(inxml):
            xmldoc = minidom.parseString(inxml)
            # use 2 spaces to indent instead of tabs
            lines = StringIO.StringIO(xmldoc.toprettyxml("  "))
            #remove redundant empty lines
            lines = [ x for x in lines if x.strip() != ""]
            return "".join(lines)

        def has_child(node):
            return node.get('name') in map(operator.itemgetter(0), links)
        def has_parent(node):
            return node.get('name') in map(operator.itemgetter(1), links)

        for parent in config.getiterator():
            for node in parent:
                if node.tag == "node":
                    node_info = dict(type=node.get('type', 'adapter'),
                                     source=node.get('from', 'plugin'),
                                     pluginname=node.get('pluginname'),
                                     name=node.get('name'))

                    if node.get('position'):
                        node_info['x'], node_info['y'] = map(int, node.get('position').split(','))

                    if node_info['source'] == 'code' and all_infos:
                        if node.find('code') is not None:
                            node_info['code'] = node.find('code').text.strip()

                    if all_infos:
#                        temp_node = node.__copy__()
#                        if temp_node.find('children') is not None:
#                            temp_node.remove(temp_node.find('children'))
                        #new_node = ET.fromstring(prettify(ET.tostring(node)))

#                        Equivalent in normal programming :
#                        node_info['content'] = "".join([etree.tostring(n)
#                                                        for n in node
#                                                        if n.tag not in stripped_nodes])
                        conf_nodes = filter(lambda n: n.tag not in stripped_nodes,
                                            node)
                        node_info['content'] = "".join(map(etree.tostring, conf_nodes))
                        node_info['config_keys'] = dict([(sn.tag, sn.text.strip()) for sn in conf_nodes if sn.text is not None])
                        node_info['etree'] = node

                    nodes.append(node_info)
                    nodes_per_name[node.get('name')] = node_info

                    joiner_info = node.find('joiner')
                    if joiner_info is not None:
                        node_info['joiner'] = joiner_info.get('pluginname')
                        if all_infos:
                            node_info['joiner_content'] = "".join(map(etree.tostring, joiner_info))

                    children = node.findall('children/node') + node.findall('children/link')

                    if children:
                        for child in children:
                            links.append((node.get('name'), child.get('name')))

        consumers = filter(lambda node: not has_child(node), nodes)
        producers = filter(lambda node: not has_parent(node), nodes)

        if compute_position:
            levels = list()
            leveled_items = list()

            def append_items(level_number, last_height, items):
                if not len(levels) > level_number:
                    levels.append(list())

                for item in items:
                    if len(levels[level_number]) < last_height:
                        for i in range(last_height - len(levels[level_number])):
                            levels[level_number].append(None)

                    height = len(levels[level_number])

                    if not item in leveled_items:
                        levels[level_number].append(item)
                        leveled_items.append(item)

                    children = [nodes_per_name.get(node[1]) for node in links if node[0] == item.get('name')]
                    append_items(level_number + 1, height, children)

            append_items(0, 0, producers)

            for x, level in enumerate(levels):
                for y, node in enumerate(level):
                    if node is not None:
                        node['x'] = x
                        node['y'] = y

        return dict(nodes=nodes,
                    links=links)


class TubeLayer(DeclarativeBase):
    """ Tube Layers are basically modifiers for tubes.

    A tube layer is applied if the tube is called with the correct variant name.
    
    Layers are applied using :mod:`pyf.services.core.modifiers` (specifically

    Example of layer:

        .. code-block:: xml

            <modifiers>
                <modifier target="foo" action="modify">
                    <bar>new bar value</bar>
                </modifier>
                <modifier target="foo_that_will_be_deleted" action="remove" />
                <modifier target="foo" action="enclose">
                    <node name="node_that_will_contain_foo_as_a_child" type="adapter" pluginname="bar" />
                </modifier>
            </modifiers>

    Class attributes:
        - `id` : Numerical unique identifier of the layer (primary key)
        - `tube_id` : The id of the tube the layer is applied on
        - `tube` : The linked tube object
        - `name` : Unique identifier of the tube layer, used for simple retrieval
        - `display_name` : Display name of the tube layer (50 chars. max)
        - `description` : Description of the tube layer (250 chars. max)
        - `active` : Description of the tube layer (250 chars. max)
        - `variant_name` : The variant name (multiple layers can have the same variant name)
        - `last_run_date`
        - `payload` : The xml content for the modifiers.
        - `priority` :
            The priority of the layer (the lower the number, the higher the priority).
            Example:

            Layer "Foo" has variant name "barred" and priority 10,
            layer "FooBar" has variant name "barred" and priority 0...
            Layer "FooBar" will get applied before Foo.
    """

    __tablename__ = "tubelayers"
    id = Column(Integer, primary_key=True) #: toto test
    """ Numerical unique identifier of the layer (primary key) """

    tube_id = Column(Integer, ForeignKey('tubes.id'))
    """ The id of the tube the layer is applied on """

    tube = relation('Tube', backref='layers')
    """ The linked tube object """

    name = Column(Unicode(50), unique=True, nullable=False)
    """ Unique identifier of the tube layer, used for simple retrieval """

    display_name = Column(Unicode(50))
    """ Display name of the tube layer (50 chars. max) """

    description = Column(Unicode(250))
    """ Description of the tube layer (250 chars. max) """

    active = Column(Boolean, nullable=False, default=True)
    """ Boolean column, flags the tube alyer as active """

    variant_name = Column(Unicode(50))
    """ The variant name (multiple layers can have the same variant name) """

    payload = Column(TEXT)
    """ The xml content for the modifiers.
    See :mod:`pyjon.descriptors` for more info.
    """

    last_run_date = Column(DateTime, nullable=True)

    priority = Column(Integer)
    """ The priority of the layer (the lower the number, the higher the priority).

    :Example:
    Layer "Foo" has variant name "barred" and priority 10,
    layer "FooBar" has variant name "barred" and priority 0...

    Layer "FooBar" will get applied before Foo.
    """

    def get_modifier_tree(self):
        """ Returns the raw ET tree for the layer """
        tree = ET.fromstring(self.payload)
        return tree

    def apply_on_node(self, primary_node):
        from pyf.services.core.modifiers import apply_modifier_set
        return apply_modifier_set(self.get_modifier_tree(),
                                  primary_node)


class Descriptor(DeclarativeBase):
    """ Descriptor model objects are basically containers for pyjon.descriptors.Descriptor objects.
    
    """
    __tablename__ = "descriptors"
    
    #: Unique ID (auto increment primary key)
    id = Column(Integer, primary_key=True)
    
    #: Unique name for descriptor (no spaces, not special chars)
    name = Column(Unicode(50), unique=True, nullable=False)
    
    #: Display name (will be used in link text, or drop downs)
    display_name = Column(Unicode(50))
    
    #: Full text description explaining what the descriptor does (what file format is it for)
    description = Column(Unicode(250))
    
    #: pyjon.descriptors.Descriptor XML payload (TEXT type).
    #: It shouldn't contain an encoding declaration but directly the first level xml node.
    payload_xml = Column(TEXT)
    
    #: Default encoding to use with this descriptor
    default_encoding = Column(String(15), nullable=True)

    @classmethod
    def by_name(cls, name):
        return DBSession.query(cls).filter(cls.name == name).first()

    def get_descriptor_object(self, encoding=None):
        """returns the pyjon.descriptors.Descriptor instance based on the
        XML schema of the descriptor stored in the database.
        This is NOT the descriptor orm object but the real pyjon
        descriptor.

        :param encoding: the encoding used by the data flow. This is really
                         important for us because we transcode the flow in unicode.
                         If no encoding is provided, use `default_encoding`.
        :type encoding: string
        """
        if encoding is None:
            encoding = self.default_encoding

        from pyjon.descriptors import Descriptor as DescriptorObject

        payload_tree = ET.fromstring(self.payload_xml)

        logging.debug('Loading descriptor: %s' % self.display_name)
        descriptor = DescriptorObject(payload_tree, encoding)
        logging.debug('Loading descriptor: %s done' % self.display_name)

        return descriptor

class TubeStorage(DeclarativeBase):
    """
    A tube storage object is used in tubes to store info about the process.
    A good example of this is when you need to do differencial extractions.
    """
    __tablename__ = "tube_storage"

    id = Column(Integer, primary_key=True)

    identifier = Column(String(50))

    date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    key = Column(String(50))
    value = Column(Unicode(512))

    def __json__(self):
        props = dict()

        for attribute in self._sa_class_manager.mapper.c:
            key = attribute.key
            props[key] = getattr(self, key)

        return props

