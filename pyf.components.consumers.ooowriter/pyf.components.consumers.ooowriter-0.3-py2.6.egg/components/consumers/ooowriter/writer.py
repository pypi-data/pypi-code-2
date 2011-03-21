from pyf.componentized.components.multiwriter import MultipleFileWriter
from pyf.componentized.configuration.keys import SimpleKey, CompoundKey,\
    BooleanKey
from pyf.componentized.configuration.fields import SingleSelectField, InputField,\
    TextAreaField, BooleanField
    
from py3o.template import Template
from py3o.renderclient import RenderClient
import logging
import itertools

class OOoWriter(MultipleFileWriter):
    """ ODT Writer.
    It takes a template done with :ref:`py3o.template` format, stored on the filesystem.
    
    If set, will ask rendering to a :ref:`py3o.renderserver`,
    to a specified host, port, target filename and format.
    
    Available output formats are :
        * PDF (.pdf)
        * WORD97 (.doc)
        * WORD2003 (.docx)
        * DOCBOOK (.sgml)
        * HTML (.html)
    
    Example :
    
    .. code-block: xml
        <node type="consumer" pluginname="ooowriter" name="odt_writer">
            <template>/var/templates/my_template.odt</template>
            <target_filename>output.odt</target_filename>
            <!-- Now for the optionnal part : rendering -->
            <rendering host="localhost" port="8994"
                       target_filename="output.pdf"
                       format="PDF">on</rendering>
        </node>
    """
    name = "ooowriter"
    
    configuration = [SimpleKey('template',
                               label='Template Path',
                               help_text="template path"),
                     SimpleKey('target_filename', 
                               label="Target Filename",
                               default="filename.odt"),
                     CompoundKey('rendering',
                                 text_value='active',
                                 attributes={'format': 'format',
                                             'host': 'host',
                                             'port': 'port',
                                             'target_filename': 'target_filename'},
                                 fields=[SingleSelectField('active',
                                                      label='Activate Rendering',
                                                           values=['yes',
                                                                   'no'],
                                                           default='no'),
                                         InputField('target_filename',
                                                    label='Rendered Filename',
                                                    default='filename.pdf'),
                                         InputField('host',
                                                    label='Rendering Host'),
                                         InputField('port',
                                                    label='Rendering Host Port',
                                                    default='8994'),
                                         SingleSelectField('format',
                                                           label='Rendering Format',
                                                           values=['PDF',
                                                                   'WORD97',
                                                                   'WORD2003',
                                                                   'DOCBOOK',
                                                                   'HTML'],
                                                           default='PDF')])]
    
    _design_metadata_ = dict(default_width=350)
    
    def __init__(self, config_node, component_id):
        """Initialize a new XHTMLPDFWriter
        @param config: XML Node
        @type config: cElementTree.Node instance

        @param component_id: The id of the component
        @type component_id: String
        """
        self.config_node = config_node
        self.id = component_id
        
    def render(self, filename, rendering_options):
        client = RenderClient(rendering_options.get('host', 'localhost'),
                              int(rendering_options.get('port', '8994')))
        output_filename = self.get_output_filename(
                                        rendering_options['target_filename'])
        client.render(filename, output_filename, rendering_options['format'])

    def write(self, values, key, output_filename, target_filename):
        self.in_count = 0
        def increment_input_count(val):
            for v in val:
                self.in_count += 1
                yield v
        
        template = Template(self.get_config_key('template'),
                            output_filename)
        
        rendering_options = self.get_config_key('rendering')
        do_rendering = rendering_options['active'].lower() in ['yes',
                                                               'true',
                                                               'on']
        values = increment_input_count(values)
        first_packet = values.next()
        values = itertools.chain([first_packet], values)
        
        status_flow = template.render_flow(dict(
                    file_name = target_filename,
                    datas = values,
                    first_packet = first_packet,
                    get_config_key = self.get_config_key,
                    key=key))

        for status in status_flow:
            if status:
                for fill in range(self.in_count):
                    yield True
                self.in_count = 0
            else:
                yield status
        
        if do_rendering:
            self.message_callback("ODT generation complete, trying to render.")
            try:
                self.render(output_filename, rendering_options)
            except Exception, e:
                logging.exception(e)
                self.message_callback("Rendering failed: %s" % e, message_type="error")
            yield True
