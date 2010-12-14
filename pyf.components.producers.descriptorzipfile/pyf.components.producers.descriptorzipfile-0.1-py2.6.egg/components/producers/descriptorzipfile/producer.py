"""
This is a simple producer taking a zipfile as input and reading the files
within it with a descriptor.
"""
import decimal
import StringIO
import zipfile

from pyf.componentized.components import Producer

import logging
log = logging.getLogger(__name__)


class DescriptorZipFile(Producer):
    """ This class is used to extract some datas from files or generator
    and return a generator that will be feeded to the pyf components paths.
    """
    name = "descriptorzipfile"
    configuration = []

    def __init__(self, config_node, process_name):
        """ Initialize the Descriptor File Extractor
        @param config_node: Configuration
        @type config_node: ET instance

        @param process name: Current process name
        @type process name: string
        """
        super(DescriptorZipFile, self).__init__(config_node, process_name)
    
    def launch(self,
               progression_callback=None,
               message_callback=None,
               params=None):
        """
        Extracts the data from files contained in a Zip archive using the
        passed descriptor.
        
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

        if params and 'descriptor' in params:
            descriptor = params['descriptor']

        else:
            raise ValueError("You need to pass a descriptor as input")

        if params and 'source' in params:
            source = params['source']
        else:
            raise ValueError("You need to pass a zip file as input")

        source_archive = zipfile.ZipFile(source, compression=zipfile.ZIP_DEFLATED)
        filelist = source_archive.namelist()

        d100 = decimal.Decimal("100")
        filestep = d100 / len(filelist)
        fileindex = 0

        for filename in filelist:
            fileindex += 1

            source_file = StringIO.StringIO(source_archive.read(filename))

            record_count = None
            if hasattr(descriptor, 'get_record_count'):
                record_count = descriptor.get_record_count(source_file)

            for index, item in enumerate(descriptor.read(source_file)):
                if record_count is not None:
                    if not (index % 500):
                        progression_callback(filestep*fileindex / record_count*index)
                    
                item.orig_filename = filename
                yield item
    
        source_archive.close()

        progression_callback(d100)

