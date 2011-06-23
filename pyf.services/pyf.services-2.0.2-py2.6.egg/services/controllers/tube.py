# -*- coding: utf-8 -*-
"""Crud Tube Controllers"""

from tg import expose, flash, require, request, redirect, validate
from formencode import validators
from pylons import tmpl_context
from pyjon.utils import indent
from pyf.services.model import DBSession
from pyf.services import model
from pyf.services.model import Tube
from pylons.controllers.util import abort

from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller

from pyf.services.controllers.crud import (SecureCrudRestController, DataGrid,
                                     render_boolean, render_link_field,
                                     has_model_permission, itemize)

from pyf.services.controllers.crud import FancyTableFiller as TableFiller
from pyf.services.controllers.tubelayer import (tubelayer_table,
                                                tubelayer_table_filler)

from pyf.services.core.events import create_event_track, get_logger
from pyf.services.core.router import Router
from pyf.services.core.tasks import launch_tube
from pyf.services.versionning.base import get_repository
from pyf.services.versionning.check import check_tube

from pyf.transport import decode_packet_flow

from repoze.what.predicates import NotAuthorizedError

from operator import itemgetter
from pyf.services.controllers.widgets import TubeLauncher

from tgscheduler.scheduler import add_single_task

import simplejson

import transaction
import time

import tw.forms

from pyf.componentized import ET
from pyf.componentized.components.resource import ResourceManager
import operator

import logging
from tg.decorators import with_trailing_slash, paginate
from genshi.template.markup import MarkupTemplate
log = logging.getLogger('pyf.services')

class TubeController(SecureCrudRestController):
    model = Tube
    __post_to_versionning__ = True
    __order_by__ = 'name'
    __desc__ = False

    class new_form_type(AddRecordForm):
        __model__ = Tube
        __omit_fields__ = ['dispatchs', 'layers']
        __require_fields__ = ['name', 'display_name', 'payload_ini']

        payload = tw.forms.TextArea('payload',
                                    default="""<config>
  <process name="main">
    <!-- this is if you need a source
    (if you don't, change the pluginname or do a from="code" and add a <code> inside): -->
    <node type="producer" pluginname="descriptorsource" name="source">
      <children>
        <node type="">
        </node>
      </children>
    </node>
  </process>
  <!-- Uncomment if you need a post process: -->
  <!--<postprocess>
  </postprocess>-->
</config>""")

    class edit_form_type(EditableForm):
        __model__ = Tube

    class edit_filler_type(EditFormFiller):
        __model__ = Tube

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
        __model__ = Tube
        __omit_fields__ = ['id', 'payload', 'description', 'events']
        __xml_fields__ = ['actions', 'dispatchs', 'active', 'needs_source']
#        __field_order__ = ['__actions__', 'active', 'name', 'display_name',
#                           'needs_source', 'variants',
#                           'last_run_date', 'dispatchs', 'tasks']

    class table_filler_type(TableFiller):
        __model__ = Tube
        __actions_size__ = "80px"
        __other_links__ = """
            <a href="${base_url}${pklist}/edit"
               style="text-decoration:none">
               <img src="/images/silk/cog_code.png" alt="xml edit" />
            </a>"""

        #layers = render_link_field('/tubelayers/%s/edit', 'layers', 'display_name')
        def layers(self, object):
            variant_names = list()
            for layer in object.layers:
                if not layer.variant_name in variant_names:
                    variant_names.append(layer.variant_name)
            variant_names.sort()
            return ', '.join(variant_names)

        def __actions__(self, obj):
            """Display standard delete and edit actions as clickable fam fam icons."""
            primary_fields = self.__provider__.get_primary_fields(self.__entity__)
            pklist = '/'.join(map(lambda x: str(getattr(obj, x)), primary_fields))
            entityname = str(obj.__class__).split('.')[-1][:-2]
            action_template = """\
            <div style="min-width:%s;min-height:16px">
                <div class="sproxactions">
                    <form method="post" action="${base_url}${pklist}" class="button-to">
                        <input type="hidden" name="_method" value="DELETE" />
                        <input
                           class="delete-button"
                           onclick="return confirm('Delete ${item} #${itemid}?');"
                           value=""
                           type="submit"
                           style="background:url('/images/silk/${itype}_delete.png') no-repeat;"/>
                    </form>
                </div>
                <div style="float:right;display:inline;">
                    <a href="${base_url}design/${pklist}" style="text-decoration:none"
                        ><img src="/images/silk/${itype}_edit.png" alt="edit" /></a>
                        %s
                    <a href="${base_url}${pklist}" style="text-decoration:none"
                        ><img src="/images/silk/${itype}_go.png" alt="view" /></a>
                </div>
            </div>""" % (self.__actions_size__, (self.__other_links__ or ""))
            return MarkupTemplate(action_template).generate(
                                                    pklist=pklist,
                                                    base_url=self.__base_url__,
                                                    itype=itemize(entityname.lower()),
                                                    item=entityname,
                                                    itemid=obj.id)

        dispatchs = render_link_field('/dispatchs/%s', 'dispatchs', 'display_name')
        active = render_boolean('active')
        needs_source = render_boolean('needs_source')

    @has_model_permission('view')
    @expose('pyf.services.templates.tube.get_one')
    @expose('json')
    def get_one(self, tube_id, action=None, **kwargs):
        if action:
            return getattr(self, action)(tube_id, **kwargs)

        tmpl_context.widget = tubelayer_table

        tube = DBSession.query(Tube).get(tube_id)

        tmpl_context.launcher = TubeLauncher(tube_id)

        layers_value = tubelayer_table_filler.get_value(tube=tube)
        return dict(tube=tube, value=tube, layers_value=layers_value)

    @has_model_permission('view')
    @expose('pyf.services.templates.tube.get_one')
    @expose('json')
    def by_name(self, name):
        tube = DBSession.query(Tube).filter(Tube.name==name).first()
        if tube is None:
            abort(404, comment="There is no tube with name %s" % name)
        return self.get_one(tube.id)

    @has_model_permission('edit')
    @expose('pyf.services.templates.tube.edit')
    def edit(self, *args, **kwargs):
        return SecureCrudRestController.edit(self, *args, **kwargs)

    @has_model_permission('create')
    @expose('pyf.services.templates.tube.edit')
    def new(self, *args, **kwargs):
        return SecureCrudRestController.new(self, *args, **kwargs)

    @has_model_permission('view')
    @with_trailing_slash
    @paginate('value_list', items_per_page=20)
    @expose('pyf.services.templates.tube.get_all')
    @expose('json')
    def get_all(self, *args, **kwargs):
        return SecureCrudRestController.get_all(self, *args, **kwargs)

    @has_model_permission('launch')
    @expose()
    @expose('json')
    @validate(validators={
            'tube_id': validators.Int(not_none=True),
            'packets': validators.FieldStorageUploadConverter()
    })
    def launch(self, tube_id, variant=None, options=None, packets=None, **kwargs):
        user_name = request.identity['repoze.who.userid']

        # Trying to see if there is a newer version on the repo...
        repository = get_repository()
        tube = DBSession.query(Tube).get(tube_id)
        check_tube(repository, tube, variant=variant)

        if options is not None:
            options = simplejson.loads(options)

        if kwargs is not None:
            if options is not None:
                options.update(kwargs)
            else:
                options = kwargs

        if options is not None:
            # grouping params in fieldsets modifies the param key
            # e.g param 'bar' in fieldset 'foo' becomes 'foo.bar' in options
            # FIXME: group params without modifying the key
            options_copy = dict(options)
            for key in options:
                if '.' in key:
                    value = options_copy.pop(key)
                    new_key = key.rsplit('.', -1)[-1]
                    options_copy[new_key] = value

            options = options_copy

            valid_options = tube.get_valid_options()

            for key in options:
                if key not in valid_options:
                    raise NotAuthorizedError, "You can't set option %s" % key

        if packets is not None:
            packets = decode_packet_flow(packets.file)

        if variant == "no_variant":
            variant = None

        event_track_id = launch_tube(tube_id,
                                     user_name=user_name,
                                     variant=variant,
                                     defered=True,
                                     options=options,
                                     source=packets)

        time.sleep(1)

        if request.response_type == 'application/json':
            return dict(event_track_id=event_track_id)

        redirect('/events/%s' % event_track_id)

    @has_model_permission('view')
    @expose('json')
    def get_parameters(self, tube_id):
        tube = DBSession.query(Tube).get(tube_id)
        return dict(value=tube.get_parameters())

    @has_model_permission('view')
    @expose('json')
    def graph(self, tube_id):
        tube = DBSession.query(Tube).get(tube_id)

        tube_dict = dict(name=tube.display_name,
                         id="tube_%s" % tube.id,
                         data=dict(type="tube"),
                         children=list())

        variant_names = tube.variant_names

        tube_dict['children'].append(dict(
            name="default",
            id="var_default",
            data=dict(type="variant"),
            children=[tube.get_graph()]
        ))

        for name in variant_names:
            tube_dict['children'].append(dict(
                name=name,
                id="var_%s"%name,
                data=dict(type="variant"),
                children=[tube.get_graph(variant=name)]
            ))

        return tube_dict

    @expose('pyf.services.templates.tube.design')
    def design(self, tube_id=None):
        if tube_id:
            tube = DBSession.query(Tube).get(tube_id)
        else:
            tube = None

        return dict(tube=tube)

    @has_model_permission('view')
    @expose('json')
    def get_graph(self, tube_id):
        try:
            tube = DBSession.query(Tube).get(tube_id)

            infos = tube.get_network_graph(full_tree=False,
                                           all_infos=True,
                                           compute_position=False)

            nodes = infos.get('nodes')
            links = infos.get('links')

            modules = list()
            name_to_module_id = dict()
            wires = list()

            resource_manager = ResourceManager()

            for node in nodes:
                item_id = len(modules)

                module_type = "%s %s" % (node.get('type'),
                                         node.get('source','plugin'))

                value_info = dict(code=node.get('code'),
                                  content=node.get('content'),
                                  joiner=dict(joiner_type=node.get('joiner', 'linear'),
                                              content=node.get('joiner_content', '')))

                if node.get('source', 'plugin') == 'plugin':
                    getter = getattr(resource_manager, 'get_%s' % node.get('type'))
                    module_class = getter(node.get('pluginname'))

                    if getattr(module_class, 'configuration', None) is not None:
                        module_type = '%s.%s.%s' % (resource_manager.main_namespace,
                                                    dict(resource_manager.plugin_types)[node.get('type')],
                                                    node.get('pluginname'))
                        for configuration_key in module_class.configuration:
                            if hasattr(configuration_key, 'gets_node_list')\
                                and configuration_key.gets_node_list:
                                node_key = node.get('etree').findall(configuration_key.key)

                            else:
                                node_key = node.get('etree').find(configuration_key.key)

                            value_info[configuration_key.key] = configuration_key.from_xml(node_key)
                else:
                    value_info['config_keys'] = [[key, value]
                                                 for key, value
                                                 in node.get('config_keys', dict()).iteritems()]
                
                # since name is a special case, don't treat it normally
                value_info.pop('name', None)
                
                modules.append(dict(name=module_type,
                                    value=dict(name=node.get('name'),
                                               plugin=node.get('pluginname'),
                                               **value_info),
                                    config=dict(
                                        position=[node.get('x', 0),
                                                  node.get('y', 0)]
                                    )
                                   )
                               )
                name_to_module_id[node.get('name')] = item_id

            for parent, child in links:
                wires.append(dict(src=dict(moduleId=name_to_module_id[parent],
                                           terminal="out"),
                                  tgt=dict(moduleId=name_to_module_id[child],
                                           terminal="in")))

            return dict(status="success",
                        modules=modules,
                        wires=wires)
        except Exception, e:
            log.exception(e)
            return dict(status="error",
                        reason=unicode(e))

#        if jsonp:
#            return "%s = %s;" % (jsonp, simplejson.dumps(return_content))
#        else:
#            return simplejson.dumps(return_content)
#        return dict(tube=tube)

    @has_model_permission('edit')
    @expose('json')
    def save_graph(self, tube_id=None, payload=None):
        try:
            payload = simplejson.loads(payload)

            if tube_id == '0':
                tube_id = None

            if tube_id:
                tube = DBSession.query(Tube).get(tube_id)
            else:
                tube = Tube(payload="""<config><process name="main" /></config>""")

            resource_manager = ResourceManager()

            from lxml import etree
            parser = etree.XMLParser(strip_cdata=False)
            tree = etree.fromstring(tube.payload, parser=parser)

            process = tree.find('process')

            for node in list(process.findall('node')) + list(process.findall('comment')):
                process.remove(node)

            nodes = list()
            links = list()

            for module in payload['modules']:
                if module.get('name') == "comment":
                    el = etree.SubElement(process, 'comment',
                                       position = ','.join(map(str,
                                                               module.get('config').get('position'))))
                    el.text = module['value']['comment']
                    continue

                is_gui_plugin = False

                if module.get('name').startswith(resource_manager.main_namespace):
                    is_gui_plugin = True

                    module_source = 'plugin'
                    module_type_ns = module.get('name').split('.')[-2]
                    module_type = dict([(b, a) for a, b in resource_manager.plugin_types])[module_type_ns]
                    getter = getattr(resource_manager, 'get_%s' % module_type)
                    plugin_name = module.get('name').split('.')[-1]
                    module_class = getter(plugin_name)
                else:
                    module_type, module_source = module.get('name').split(' ')

                module_values = module.get('value')

                el = etree.SubElement(process, 'node', **{'from': module_source,
                                                       'type': module_type,
                                                       'name': module_values.get('name'),
                                                       'position': ','.join(map(str, module.get('config').get('position')))})

                if module_values.get('joiner'):
                    joiner_info = module_values.get('joiner')
                    joiner_node = etree.SubElement(el, 'joiner', pluginname=joiner_info.get('joiner_type', ''))
                    if joiner_info.get('content'):
                        try:
                            for enode in etree.fromstring('<content>%s</content>' % joiner_info.get('content'), parser=parser):
                                joiner_node.append(enode)
                        except SyntaxError:
                            return dict(status="error",
                                        reason="bad formed xml in joiner node of %s" % module_values.get('name'))

                if is_gui_plugin:
                    el.set('pluginname', plugin_name)
                    for configuration_key in module_class.configuration:
                        if configuration_key.key != 'name':
                            node = configuration_key.to_xml(module_values.get(configuration_key.key))
                            if isinstance(node, list):
                                for node_el in node:
                                    el.append(node_el)

                            elif node is not None:
                                el.append(node)

                else:
                    if module_source == 'plugin':
                        el.set('pluginname', module_values.get('plugin'))
                    elif module_source == 'code':
                        code_el = etree.SubElement(el, 'code')
                        code_el.text = etree.CDATA(module_values.get('code'))

                    if module_values.get('content'):
                        try:
                            for enode in etree.fromstring('<content>%s</content>' % module_values.get('content'), parser=parser):
                                el.append(enode)
                        except SyntaxError:
                            return dict(status="error",
                                        reason="bad formed xml in node %s" % module_values.get('name'))

                    if module_values.get('config_keys'):
                        for key, value in module_values.get('config_keys'):
                            conf_key_el = etree.SubElement(el, key)
                            conf_key_el.text = value

                nodes.append(el)

            for wire in payload['wires']:
                if wire.get('src').get('terminal') == 'out':
                    src = wire.get('src').get('moduleId')
                    tgt = wire.get('tgt').get('moduleId')
                else:
                    src = wire.get('tgt').get('moduleId')
                    tgt = wire.get('src').get('moduleId')

                children_node = nodes[src].find('children')
                if children_node is None:
                    children_node = etree.SubElement(nodes[src], 'children')

                links.append(etree.SubElement(children_node, 'link', name=nodes[tgt].get('name')))

            root_level = 2

            for node in nodes:
                indent(node, root_level)

            tube.payload = unicode(etree.tostring(tree))

            if payload.get('properties'):
                # If we got properties info too...
                properties = payload.get('properties')
                tube.name = properties['name']
                tube.display_name = properties.get('display_name', tube.name)
                tube.active = properties.get('active', False)
                tube.needs_source = properties.get('needs_source', False)
            else:
                if tube_id is None:
                    return dict(status="error",
                                reason="Trying to create a tube without specifying properties")

            DBSession.add(tube)
            DBSession.flush()

            get_repository().store_item(tube, user=request.identity['user'].user_name)

            return dict(status="success",
                        tube_id=Tube.by_name(tube.name).id)

        except Exception, e:
            log.exception(e)
            return dict(status="error",
                        reason=unicode(e))

    @has_model_permission('view')
    @expose()
    def language_definition(self, jsonp=""):
        return_content = dict(modules=list())

        resource_manager = ResourceManager()

        plugins = resource_manager.get_plugins()

        terminals_definition = [{
            "name": "out",
            "direction": [0, 1],
            "offsetPosition": {
                "left": 86,
                "bottom": -15
            },
            "ddConfig": {
                "type": "output",
                "allowedTypes": ["input"]
            },
            "editable": True
        }, {
            "name": "in",
            "direction": [0, -1],
            "fakeDirection": [0, 1],
            "offsetPosition": {
                "left": 82,
                "top": -15
            },
            "ddConfig": {
                "type": "input",
                "allowedTypes": ["output"]
            }
        }]

        joiner_plugins_list = plugins['joiners']
        joiner_plugin_names = [pname for pname, pclass in  joiner_plugins_list]

        for plugin_type, plugin_list in plugins.iteritems():
            if plugin_type == "joiners":
                # for now, we don't expose joiners...
                # TODO: find a good way to expose them.
                continue

            if plugin_type == 'producers':
                terminals = terminals_definition[:1]
#            elif plugin_type == 'consumers':
#                terminals = terminals_definition[1:]
            else:
                terminals = terminals_definition

            for plugin_name, plugin in plugin_list:
                if hasattr(plugin, 'configuration') and plugin.configuration is not None:
                    fields = []
#                        {
#                            "type": "input",
#                            "inputParams": {
#                                "label": "Name",
#                                "name": "name",
#                                "wirable": False,
#                                "typeInvite": "unique name"
#                            }
#                        }
#                    ]
                    if plugin_type != 'producers':
                        fields.insert(0, {
                            "type": "group",
                            "inputParams": {
                                "name" : "joiner",
                                "legend" : "Joiner Info",
                                "collapsible" : True,
                                "collapsed" : True,
                                "fields" : [
                                    {

                                        "type" : "select",
                                        "inputParams": {
                                            "label" : "Type",
                                            "name" : "joiner_type",
                                            "value" : "linear",
                                            "selectValues" : joiner_plugin_names
                                        }
                                    },
                                    {
                                        "type" : "text",
                                        "inputParams": {
                                            "name": "content",
                                            "label" : "Content",
                                            "value" : ""
#                                            "className": "xmlcode"
                                        }
                                    }
                                ]
#                                "value" : {
#                                    "joiner_type" : "linear"
#                                }
                            }
                        })

                    module_definition = dict(name='%s.%s.%s' % (resource_manager.main_namespace, plugin_type, plugin_name),
                                             container=dict(terminals=terminals,
                                                            xtype="WireIt.FormContainer",
                                                            title="Adapter",
                                                            fields=fields,
                                                            collapsible=False,
                                                            display_name=getattr(plugin, 'display_name', plugin.__name__)))
                    module_config = plugin.configuration
                    for config_key in plugin.configuration:
                        fields.append(config_key.field.get_display_info())

                    if getattr(plugin, '_design_metadata_', None) is not None:
                        for key, value in plugin._design_metadata_.iteritems():
                            module_definition['container'][key] = value

                    return_content['modules'].append(module_definition)

        if jsonp:
            return "%s = %s;" % (jsonp, simplejson.dumps(return_content))
        else:
            return simplejson.dumps(return_content)
