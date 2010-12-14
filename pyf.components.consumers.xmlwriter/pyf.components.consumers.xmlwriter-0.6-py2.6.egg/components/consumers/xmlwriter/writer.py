from genshi.template import MarkupTemplate
from pkg_resources import resource_string
from pyf.componentized.components.multiwriter import MultipleFileWriter
import codecs

from pyf.componentized.configuration.keys import SimpleKey, XMLKey, CompoundKey
from pyf.componentized.configuration.fields import TextAreaField,\
    SingleSelectField, InputField

class XMLWriter(MultipleFileWriter):
    name = "xmlwriter"
    
    configuration = [SimpleKey('encoding', default="UTF-8"),
                     SimpleKey('target_filename', default="filename.xml"),
                     CompoundKey('template',
                                 text_value='template',
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
    
    def __init__(self, config_node, component_name):
        """Initialize a new XMLWriter
        @param config: SafeConfigParser
        @type config: SafeConfigParser instance

        @param process_name: The process name to use
        @type process_name: String
        """
        self.config_node = config_node
        self.name = component_name

        self.template = self.get_template()
        
    def get_template(self):
        template_node = self.get_config_key('template')
        template_type = template_node.get('type', 'embedded')
        
        if template_type == 'plugin':
            template_module = template_node.get('module')
            return MarkupTemplate(
                       resource_string(
                           template_module,
                           "static/templates/" + template_node.get('template').strip() + ".xml"
                       )
                   )
            
        elif template_type == 'embedded':
            return MarkupTemplate(template_node.get('template').strip())

        else:
            raise NotImplementedError, "Template type %s is not handled." % \
                                                                template_type

    def write(self, values, key, output_filename, target_filename):
        encoding = self.get_config_key('encoding')
        
        target_file = codecs.open(output_filename, 'wb+', encoding)

        for num, markup in enumerate(self.template.generate(
                    file_name=target_filename,
                    splitkey=key,
                    encoding=encoding,
                    datas=values,
                    get_config_key=self.get_config_key).serialize(method='xml')):
            target_file.write(markup)
            yield True

        target_file.close()
        yield True
