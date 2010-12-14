from pyf.componentized.components.multiwriter import MultipleFileWriter
from ConfigParser import NoOptionError, NoSectionError
from genshi.template import MarkupTemplate
from pkg_resources import resource_string, resource_filename
import codecs
import collections

import ho.pisa as pisa

import logging
import os
import tempfile
from pyf.componentized.configuration.keys import SimpleKey, CompoundKey
from pyf.componentized.configuration.fields import SingleSelectField, InputField,\
    TextAreaField
log = logging.getLogger()

class ReportTemplate(MarkupTemplate):
    def write(self, target_file, **kwargs):
        for status in self.process_write(target_file, **kwargs):
            if not status:
                raise Exception, "Error in file writing"
        if 'should_close' in kwargs and kwargs['should_close']:
            target_file.close()
    
    def __generate_tempfile(self):
        fd, fname = tempfile.mkstemp()
        os.close(fd)
        return fname
    
    def __clean_tempfile(self, filename):
        os.unlink(filename)
        
    def process_write(self, target_file, **kwargs):
        """ Do the process of writing the RML file while yielding statuses... """
        flow = self.generate(**kwargs)
        for markup in flow.serialize():
            target_file.write(markup)
            yield True
    
    def render(self, outfilename, **kwargs):
        """ Renders the report template to pdf with the given kwargs.
        
        Warning: This function does a sleep between genshi rendering and PDF gen
        to avoid crash of rml2pdf.
        
        @param outfilename: the filename of the pdf to write.
        @type outfilename: string
        
        @kwargs: all the vars you want to pass to genshi context
        """
        
        # Creating temp file for rml output
        temp_fname = self.__generate_tempfile()
        temp_file = codecs.open(temp_fname, 'wb+', 'utf-8')
        
        # Writing XML output
        self.write(temp_file, should_close=True, **kwargs)
        
        # Writing PDF from XHTML
        
        result = pisa.CreatePDF(open(temp_fname, 'rb'), open(outfilename, 'wb'))
        
        # Cleaning temp file
        self.__clean_tempfile(temp_fname)
        
        return result.err
    
    def render_flow(self, outfilename, **kwargs):
        """ Renders the report template to pdf with the given kwargs while
        yielding statuses.
        
        @param outfilename: the filename of the pdf to write.
        @type outfilename: string
        
        @kwargs: all the vars you want to pass to genshi context
        """
        
        # Creating temp file for rml output
        temp_fname = self.__generate_tempfile()
        temp_file = codecs.open(temp_fname, 'wb+', 'utf-8')
        
        yield True
        
        # Writing RML output
        for status in self.process_write(temp_file, **kwargs):
            yield status
        
        temp_file.close()
        yield True
        pisa.showLogging()
        # Writing PDF from XHTML
        outfile = open(outfilename, 'wb')
#        StringIO.StringIO(html.encode("UTF-8"))
        result = pisa.CreatePDF(open(temp_fname, 'rb'), outfile)
        outfile.close()
        yield (not bool(result.err))
        
        # Cleaning temp file
        self.__clean_tempfile(temp_fname)
        yield True

class XHTMLPDFWriter(MultipleFileWriter):
    name = "xhtmlpdfwriter"
    
    configuration = [SimpleKey('encoding', default="UTF-8"),
                     SimpleKey('target_filename', default="filename.pdf"),
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

    def __init__(self, config_node, component_id):
        """Initialize a new XHTMLPDFWriter
        @param config: XML Node
        @type config: cElementTree.Node instance

        @param component_id: The id of the component
        @type component_id: String
        """
        self.config_node = config_node
        self.id = component_id

        self.encoding = self.get_config_key('encoding', 'UTF-8')

        self.template = self.get_template()
        
    def get_template(self):
        template_node = self.get_config_key('template')
        template_type = template_node.get('type', 'embedded')
        
        if template_type == 'plugin':
            template_module = template_node.get('module')
            return ReportTemplate(
                       resource_string(
                           template_module,
                           "static/templates/" + template_node.text.strip() + ".html"
                       )
                   )
            
        elif template_type == 'embedded':
            return ReportTemplate(template_node.get('template'))
        
        else:
            raise NotImplementedError, "Template type %s is not handled." % \
                                                                template_type

    def get_resources_folder(self):
        template_node = self.get_config_key('template')
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
