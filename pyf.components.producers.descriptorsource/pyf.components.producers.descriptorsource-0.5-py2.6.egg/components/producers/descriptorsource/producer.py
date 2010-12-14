"""
This is a simple producer taking a file in input and reading it with a descriptor
"""

from pyf.componentized.components import Producer
from pyf.componentized import ET

from pyjon.descriptors import Descriptor

import codecs
import decimal

import logging

log = logging.getLogger(__name__)

def get_descriptor(xml_schemafile, encoding, buffersize=16384):
    """helper function to construct a descriptor instance from
    a schema file to help test implementations

    @param xml_schemafile: the filename that contains the xml schema
    that should normally be in the database but is in a static file
    for test purposes
    @type xml_schemafile: string or unicode object

    @param encoding: the encoding of the stream to read (ie: 'utf-8')
    @type encoding: string

    @param buffersize: the size of the buffer in bytes for the read operation.
    This will be used by the readers that perform buffering themselves
    @type buffersize: int
    """
    payload_tree = ET.parse(xml_schemafile)
    return Descriptor(payload_tree, encoding, buffersize=buffersize)

class DescriptorSource(Producer):
    """ This class is used to extract some datas from files or generator
    and return a generator that will be feeded to the pyf components paths.
    """
    name = "descriptorsource"
    configuration = []
    def __init__(self, config_node, process_name):
        """ Initialize the Descriptor Source Extractor
        @param config_node: Configuration
        @type config_node: ET instance

        @param process name: Current process name
        @type process name: string
        """
        super(DescriptorSource, self).__init__(config_node, process_name)
    
    def launch(self,
               progression_callback=None,
               message_callback=None,
               params=None):
        """
        Extracts the data from a file using the passed descriptor.
        If there is a data item in params, just yield it.
        
        Available params in params dict:
        - data: if provided: iterates over the lines in data and yield them.
        - descriptor: use this descriptor to read the data
        - source: use this file-like object as data source
        - source_filename: use this file as data source.
                           requires the source_encoding config key.
        """
        
        if not progression_callback:
            progression_callback = lambda x: log.debug('Progression : %s' % x)

        if not message_callback:
            message_callback = log.info
        
        progression_callback(0)
        
        if params and 'data' in params:
            for data_line in params['data']:
                yield data_line
            progression_callback(100)
        
        else:
            if params and 'descriptor' in params:
                descriptor = params['descriptor']
            else:
                if self.get_config_key('decriptor_filename'):
                    descriptor = get_descriptor(
                                        self.get_config_key('decriptor_filename'),
                                        self.get_config_key('source_encoding'))
                elif self.get_config_key('decriptor'):
                    descriptor = Descriptor(
                            ET.fromstring(self.get_config_key('decriptor')),
                            self.get_config_key('source_encoding'),
                            buffersize=self.get_config_key('buffer_size',
                                                           16384))
            
            if params and 'source' in params:
                source = params['source']
            else:
                source_filename = None
                if params and 'source_filename' in params:
                    source_filename = params['source_filename']
                else:
                    source_filename = self.get_config_key('source_filename')
                    
                if params and 'source_encoding' in params:
                    source_encoding = params['source_encoding']
                else:
                    source_encoding = self.get_config_key('source_encoding')
                
                source = codecs.open(source_filename, 'r',
                                     encoding=source_encoding)
            
            record_count = None
            if hasattr(descriptor, 'get_record_count'):
                record_count = descriptor.get_record_count(source)
            
            d100 = decimal.Decimal("100")
            for index, item in enumerate(descriptor.read(source)):
                if record_count is not None:
                    if not (index % 500):
                        progression_callback(d100/record_count*index)
                        
                yield item
                
            progression_callback(100)
