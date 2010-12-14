"""
This is a simple producer taking a folder as input and reading the files
within it with a descriptor.
"""
import codecs
import decimal
import fnmatch
import logging
import os
import datetime

from pyjon.utils import substitute

from pyf.componentized.components import Producer
from pyf.componentized.configuration.keys import SimpleKey
from pyf.services.model import Descriptor

log = logging.getLogger(__name__)


class DescriptorFromFolder(Producer):
    """ This class is used to extract some datas from files or generator
    and return a generator that will be feeded to the pyf components paths.
    """
    name = "descriptorfromfolder"
    configuration = [SimpleKey('input_folder', label="Input Folder"),
                     SimpleKey('pattern',
                               label="Pattern matching the files names (optional)"),
                     SimpleKey('encoding', label="Encoding of the files",
                               default="UTF-8"),
                     SimpleKey('descriptor',
                               label="Name of the descriptor to use"),
                     ]

    def __init__(self, config_node, process_name):
        """ Initialize the Descriptor File Extractor
        @param config_node: Configuration
        @type config_node: ET instance

        @param process name: Current process name
        @type process name: string
        """
        super(DescriptorFromFolder, self).__init__(config_node, process_name)

    def __get_files(self):
        """Recursively walk the input folder and yield file-like objects

        Note: The caller needs to take care of properly closing the files.
        """
        files = list()

        for root_folder, sub_folders, filenames in os.walk(self.input_folder):
            for filename in filenames:
                if fnmatch.fnmatch(filename, self.pattern):
                    full_path = os.path.join(root_folder, filename)
                    files.append(codecs.open(full_path, 'r', encoding=self.encoding))

        return files

    def launch(self,
               progression_callback=None,
               message_callback=None,
               params=None):
        """
        Read the data from files contained in a folder using the passed
        descriptor.
        
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

        self.input_folder = self.get_config_key('input_folder')
        self.encoding = self.get_config_key('encoding')
        if not self.encoding:
            raise ValueError("You must specify an encoding")

        self.pattern = substitute(self.get_config_key('pattern'), self.get_config_key)
        self.pattern = substitute(self.pattern, lambda x: eval(x), regex=r"\|([^|]+?)\|")
        if not self.pattern:
            self.pattern = "*"

        filelist = self.__get_files()

        d100 = decimal.Decimal("100")

        if bool(filelist):
            descriptor = Descriptor.by_name(
                    self.get_config_key('descriptor')).get_descriptor_object(
                            encoding=self.encoding)

            filestep = d100 / len(list(filelist))

            for fileindex, source_file in enumerate(filelist):
                record_count = None
                if hasattr(descriptor, 'get_record_count'):
                    record_count = descriptor.get_record_count(source_file)

                for index, item in enumerate(descriptor.read(source_file)):
                    if record_count is not None:
                        if not (index % 500):
                            progression_callback((fileindex + index/record_count)*filestep)
                        
                    item.orig_filename = source_file.name
                    yield item

                progression_callback((fileindex+1)*filestep)

        progression_callback(d100)

