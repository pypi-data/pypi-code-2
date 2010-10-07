import os
import logging
import csv
import re
from csv import DictWriter
import shutil
import codecs
import datetime
import tempfile
from ConfigParser import SafeConfigParser
from pyjon.utils import get_secure_filename

log = logging.getLogger(__name__)

class Any2FixedError(Exception):
    """the base class for all exceptions raised by Any2Fixed
    """
    pass

class FieldLenError(Any2FixedError):
    """this exception is raised when a field cannot
    be constained to the max len it has been assigned
    """
    pass

class FieldMappingError(Any2FixedError):
    """this exception is raised when the configuration of
    a field mapping is erroneous
    """
    pass

def recursive_getattr(obj, attr, default_value=None):
    if hasattr(obj, attr):
        return getattr(obj, attr)

    if not '.' in attr:
        return default_value

    newattr, tail = attr.split('.', 1)
    if not hasattr(obj, newattr):
        return default_value

    new_obj = getattr(obj, newattr)
    return recursive_getattr(new_obj, tail, default_value)

class FixedAddon(object):

    def __init__(self, obj, field_mappings, encoding):
        """
        @param obj: The adapted object
        @type obj: ObjectAdapter instance

        @param field_mappings: a list of dictionnary with keys containing the
        information needed to transform the data that will be passed in
        the write method into fixed length file
        @type field_mappings: list of dictionnary

        @param encoding: Encoding to use to encode all strings before serialize
        @type encoding: String
        """
        self.obj = obj
        self.field_mappings = field_mappings
        self.encoding = encoding

        self.__field_maps = dict()
        self.__init_field_maps()

    def __init_field_maps(self):
        for fieldmap in self.field_mappings:
            self.__field_maps[fieldmap['fieldname']] = fieldmap

    def keys(self):
        """Dictionnary method needed by the DictWriter
        """
        return self.__field_maps.keys()

    def encode(self, data):
        if isinstance(data, unicode):
            value = data.encode(self.encoding)
            try:
                unicode(value)
                return value
            except UnicodeError:
                return data
        else:
            return data

    def get(self, field_name, default_value):
        """Dictionnary method. default value is mandatory
        """
        field_mapping = self.__field_maps[field_name]
        attr = field_mapping.get('attr', None)
        renderer = field_mapping.get('renderer', None)
        
        if not attr is None:
            data = recursive_getattr(self.obj, attr, default_value)
            #data = self.encode(data)

        else:
            data = None

        if not renderer is None:
            if callable(renderer):
                data = renderer(data)
            elif isinstance(renderer, str) or\
                    isinstance(renderer, unicode):
                data = renderer

        return data

class Any2Fixed(object):

    def __init__(self, target_filename, field_mappings,
            encoding='UTF-8', linesep="\r\n"):
        """
        @param target_filename: The target file name
        @type target_filename: String

        @param field_mappings: Mapping to use
        @type field_mappings: list of dictionnary with keys : 
            - attr
            - colname
            - renderer (callback function or string)

            The renderer callback must accept one argument: the original object,
            and must return a unicode object.

        @param encoding: The encoding to use to write the final file
        @type encoding: String

        @param linesep: the line separator to use in the resulting file
        @type linesep: string
        """
        self.encoding = encoding
        self.target_filename = target_filename
        self.field_mappings = field_mappings
        self.check_field_mappings()
        self.linesep = linesep

        self.__tmp_filename = get_secure_filename()
        self.__tmp_file = codecs.open(
                self.__tmp_filename, 'wb+', encoding=self.encoding)

    def check_field_mappings(self):
        """this is a checking function only, it will raise a FieldMappingError
        exception is case of any problem in the field mappings given by
        the user
        """
        for field_mapping in self.field_mappings:
            attr = field_mapping.get('attr', None)
            renderer = field_mapping.get('renderer', None)
            fieldname = field_mapping.get('fieldname', None)

        if fieldname is None:
            raise FieldMappingError(
                    'The fieldname is mandatory on the fieldname mapping')

        if not renderer is None:
            if not (isinstance(renderer, str) or \
                    isinstance(renderer, unicode) or \
                    callable(renderer)):
                msg = "Renderer definition error from the field mapping,"
                msg += " renderer must be only string/unicode or callable,"
                msg += "not %s" % type(renderer)

                raise FieldMappingError(msg)

        if renderer is None and attr is None:
            msg = 'On the field mapping definition,'
            msg += ' you must define at least attr or renderer'
            raise FieldMappingError(msg)

        if attr is None and callable(renderer):
            msg = 'You cannot use a callable renderer if attr is not defined.'
            raise FieldMappingError(msg)

    def __get_column_attributes(self):
        return [col_def['attr'] for col_def in self.column_mappings]

    def __get_column_names(self):
        return [col_def['colname'] for col_def in self.column_mappings]

    def write(self, data_generator):
        """this public method will consume the data generator that
        has been passed to it and will adapt each object to make sure
        it gets written to the fixed length file.

        this function does not return anything. At the end of the run
        the desired target file is moved to the place were it has been
        requested at instanciation time.
        """
        for data in data_generator:
            self.writeline(data)
        
        self.finalize()

    def writeline(self, data):
        adapted_data = FixedAddon(data, self.field_mappings, self.encoding)
        resultline = ''
        # Write data here
        for mapping in self.field_mappings:
            name = mapping.get('fieldname')
            resultline += adapted_data.get(name, None)

        resultline += self.linesep
        self.__tmp_file.write(resultline)

    def finalize(self):
        self.__tmp_file.close()
        self.__write_target_file(self.__tmp_filename)

    def __write_target_file(self, temp_filename):
        shutil.move(temp_filename, self.target_filename)


