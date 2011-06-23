from pyf.componentized.error import MissingConfigEntryError, MissingConfigSectionError
from pyf.componentized.components.writer import BaseFileWriter
from pyf.componentized.components.multiwriter import MultipleFileWriter
from ConfigParser import NoOptionError, NoSectionError
from genshi.template import Template, MarkupTemplate
from pkg_resources import resource_string, resource_filename
from pyjon.reports import ReportTemplate, ReportFactory
import codecs
import collections
from itertools import chain
import operator

from pyf.dataflow import component, BYPASS_VALS

from lxml.etree import XMLSyntaxError

import datetime

import time

import logging
from pyf.componentized.configuration.keys import SimpleKey, CompoundKey
from pyf.componentized.configuration.fields import SingleSelectField, InputField,\
    TextAreaField
log = logging.getLogger()

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


class RMLPDFWriter(MultipleFileWriter):
    name = "rmlpdfwriter"
    
    configuration = [SimpleKey('encoding', default="UTF-8"),
                     SimpleKey('target_filename', default="filename.pdf"),
                     CompoundKey('template',
                                 text_value='template',
                                 text_as_cdata=True,
                                 attributes={'type': 'type',
                                             'module': 'module'},
                                 fields=[SingleSelectField('type',
                                                           label='Template Type',
                                                           values=['embedded', 'plugin'],
                                                           default='embedded'),
                                         InputField('module',
                                                    label='Plugin Module',
                                                    help_text='Use only for type "plugin"'),
                                         TextAreaField('template', classname="xmlcode")])]

    def __init__(self, config_node, component_id):
        """Initialize a new RMLPDFWriter
        @param config: SafeConfigParser
        @type config: SafeConfigParser instance

        @param process_name: The process name to use
        @type process_name: String
        """
        self.config_node = config_node
        self.id = component_id

        self.encoding = self.get_config_key('encoding', 'UTF-8')
        self.final_target_filename = self.get_config_key('target_filename',
                                                         'report.pdf')

        self.template = self.get_template()
        
    def get_template(self):
        template_node = self.get_config_key('template')
        template_type = template_node.get('type', 'embedded')
        
        if template_type == 'plugin':
            template_module = template_node.get('module')
            return ReportTemplate(
                       resource_string(
                           template_module,
                           "static/templates/" + template_node.text.strip() + ".xml"
                       )
                   )
            
        elif template_type == 'embedded':
            return ReportTemplate(template_node.get('template'))
        
        else:
            raise NotImplementedError, "Template type %s is not handled." % \
                                                                template_type

    def get_resources_folder(self):
        template_node = self.config_node.find('template')
        template_type = template_node.get('type', 'embedded')

        if template_type == "plugin":
            template_module = template_node.get('module')
            return resource_filename(
                           template_module,
                           "static/templates/resources")

        else:
            return self.get_config_key('resources_folder')

    def write(self, values, key, output_filename, target_filename):
        self.in_count = 0
        def increment_input_count(val):
            for v in val:
                self.in_count += 1
                yield v

        status_flow = self.template.render_flow(
                    output_filename,
                    file_name=target_filename,
                    encoding=self.encoding,
                    datas=increment_input_count(values),
                    get_config_key=self.get_config_key,
                    resources_folder=self.get_resources_folder(),
                    key=key)

        for status in status_flow:
            if status:
                for fill in range(self.in_count):
                    yield True
                self.in_count = 0
            else:
                yield status


class MultiRMLPDFWriter(BaseFileWriter):
    """
    Multiple output pdf writer...

    Example of use :
    
        .. code-block:: xml
        
            <node type="consumer" pluginname="multirmlpdfwriter" name="pdf_report">
                <encoding>UTF-8</encoding>
                <target_filename>myreport.pdf</target_filename>
                <document>
                    <part>
                        <template type="plugin" module="foo">introduction</template>
                    </part>
                    <part type="multiple">
                        <expression>item.error_type</expression>
                        <template type="plugin" module="foo">error_type</template>
                    </part>
                    <part>
                        <template type="plugin" module="foo">footer</template>
                    </part>
                </document>
            </node>
                            """

    name = "multirmlpdfwriter"
    outputs_files = True

    def __init__(self, config_node, component_name):
        """Initialize a new MultiRMLPDFWriter
        @param config: SafeConfigParser
        @type config: SafeConfigParser instance

        @param process_name: The process name to use
        @type process_name: String
        """
        self.config_node = config_node
        self.name = component_name

        self.encoding = self.get_config_key('encoding', 'UTF-8')

        self.init_document_definition()

        self.factory = ReportFactory()

    def get_template_string(self, template_node):
        template_type = template_node.get('type', 'embedded')

        if template_type == 'plugin':
            template_module = template_node.get('module')
            return resource_string(
                           template_module,
                           "static/templates/" + template_node.text.strip() + ".xml"
                       )
        elif template_type == 'embedded':
            return template_node.text.strip()

        else:
            raise NotImplementedError, "Template type %s is not handled." % \
                                                                template_type

    def get_resources_folder(self, template_node):
        template_type = template_node.get('type', 'embedded')

        if template_type == "plugin":
            template_module = template_node.get('module')
            return resource_filename(
                           template_module,
                           "static/templates/resources")

        else:
            return self.get_config_key('resources_folder')

    def init_document_definition(self):
        self.document_node = self.get_config_key_node('document')
        self.document_definition = list()
        for part_node in self.document_node.findall('part'):
            part_type = part_node.get('type', 'simple')
            expression = part_node.find('expression') is not None and part_node.find('expression').text.strip() or None
            ffilter = part_node.find('filter') is not None and part_node.find('filter').text.strip() or None
            part_def = {'type': part_type,
                        'template_node': part_node.find('template'),
                        'expression': expression,
                        'filter': ffilter}
            self.document_definition.append(part_def)

    def filter_values(self, values, expression):
        if expression is not None and expression:
            expression = compile(expression, '<string>', 'eval')
            for item in values:
                base_item = item
                if eval(expression):
                    yield item
                else:
                    yield Ellipsis
        else:
            for item in values:
                yield item

    def virtual_renderer_factory(self, values, part_num, part_def):
        added_values = list()
        expression = part_def['expression']
        if expression is not None and expression:
            expression = compile(expression, '<string>', 'eval')

            def exp_filter_values(values, value):
                for item in values:
                    base_item = item
                    if eval(expression) == value:
                        yield item
                    else:
                        yield Ellipsis

            while True:
                try:
                    item = values.next()
                    base_item = item
                    exp_result = eval(expression)
                    if exp_result not in added_values:
                        (values, myqueue), (other_values, otherqueue) = buftee(values, 2)
                        other_values = chain([item], other_values)

                        queue = collections.deque()
                        other_values = exp_filter_values(other_values,
                                                         exp_result)

                        self.add_renderer(other_values, part_def, part_num,
                                exp_result, queue, other_values.next,
                                otherqueue, document_part_key=exp_result)
                        added_values.append(exp_result)

                    yield True

                except StopIteration:
                    break
        else:
            raise ValueError("Parts of type Multiple must have an expression")

    def add_renderer(self, flow, part_def, part_num, sub_part_key, queue,
                     nexter, teebuf, **kwargs):
        renderer = self.factory.render_template_flow(template_string=self.get_template_string(part_def['template_node']),
                                                     file_name=self.final_target_filename,
                                                     encoding=self.encoding,
                                                     datas=self.prepare_input_flow(flow,
                                                                                   queue),
                                                     get_config_key=self.get_config_key,
                                                     resources_folder=self.get_resources_folder(part_def['template_node']),
                                                     **kwargs)

        # tuple with part number, sub part id (sorter), real pdf part number, renderer
        self.renderers.append((part_num, sub_part_key, self.initialized_part,
                               renderer, queue, nexter, teebuf))
        self.initialized_part += 1

    def prepare_input_flow(self, flow, inbuffer):
        while True:
            # hangs on stopiteration
            if inbuffer:
                value = inbuffer.popleft()
            else:
                value = flow.next()

            if value in BYPASS_VALS:
                # bypass_buffer.append(value)
                # TODO: if needed, implement outher direction buffer (from in to
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
                yield flow.next() # in case our main down flow is finished,
                                  # raises stopiteration too, which isn't catched.
                continue

            if up_val in BYPASS_VALS:
                yield up_val
            else:
                input_buffer.append(up_val)
                yield flow.next() # will stop on stopiteration...

    @component('IN', 'OUT')
    def launch(self, values, out):
        self.in_count = 0
        def increment_input_count(val):
            for v in val:
                self.in_count += 1
                yield v

        values = increment_input_count(values)

        self.final_target_filename = self.get_config_key('target_filename',
                                                         'report.pdf')
        self.renderers = list()
        self.burnt_sources = list()
        assert len(self.document_definition) >= 1, "You should define at least one part in the document"

        initial_tee = buftee(values, len(self.document_definition))

        self.initialized_part = 0
        for initial_tee_num, part_def in enumerate(self.document_definition):
            if part_def['type'] == 'simple':
                #bucket = Bucket()
                queue = collections.deque()
                renderer_values = \
                             self.filter_values(initial_tee[initial_tee_num][0],
                                                part_def['filter'])
                #renderer_values = bucket_fill(renderer_values, bucket, replacement_value=True)

                self.add_renderer(renderer_values, part_def, initial_tee_num,
                                  None, queue,
                                  initial_tee[initial_tee_num][0].next,
                                  initial_tee[initial_tee_num][1])

            if part_def['type'] == 'multiple':
                queue = collections.deque()
                self.renderers.append((initial_tee_num, None, None,
                                       self.virtual_renderer_factory(self.filter_values(initial_tee[initial_tee_num][0],
                                                                                        part_def['filter']),
                                                                     initial_tee_num,
                                                                     part_def),
                                       queue,
                                       initial_tee[initial_tee_num][0].next,
                                       initial_tee[initial_tee_num][1]))

        initialized_renderers = list()
        while True:
            for i in range(len(self.renderers)):
                part_num, sub_part, pdf_part, renderer, input_bucket, nexter, teebuf = self.renderers[i]
                if renderer not in initialized_renderers:
                    if sub_part is not None and pdf_part is not None:
                        renderer = self.prepare_output_flow(renderer, input_bucket, nexter)
                        rl = list(self.renderers[i])
                        rl[3] = renderer
                        self.renderers[i] = tuple(rl)

                    initialized_renderers.append(renderer)

                if not renderer in self.burnt_sources:
                    val = None
                    try:
                        while teebuf:
                            val = renderer.next()
                            if not val:
                                yield val

                        val = renderer.next()
                        if not val:
                            yield val
                    except StopIteration:
                        self.burnt_sources.append(renderer)
                        continue
                    except XMLSyntaxError:
                        self.burnt_sources.append(renderer)
                        continue
                else:
                    # In case we didn't iterate on the flow in the template
                    if teebuf:
                        teebuf.clear()

            for fill in range(self.in_count):
                yield True

            self.in_count = 0

            if len(self.burnt_sources) >= len(self.renderers):
                break

        #log.error("tempfiles: %s" % self.factory.tempfiles)

        if self.factory.tempfiles:
            self.factory.reorder_tempfiles([item[2] for item in sorted(self.renderers) if item[2] is not None])
            self.factory.render_document(self.get_output_filename(self.prepare_filename(self.final_target_filename)))

        yield True

