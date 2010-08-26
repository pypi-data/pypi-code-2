from csv import DictWriter
from pyf.componentized.components.multiwriter import MultipleFileWriter
import csv

from pyf.components.consumers.csvwriter.addon import CSVAddon

from pyf.componentized.configuration.keys import RepeatedKey, SimpleKey,\
    CompoundKey
from pyf.componentized.configuration.fields import InputField

class CSVWriter(MultipleFileWriter):
    name = "csvwriter"
    
    configuration = [SimpleKey('encoding', default="UTF-8"),
                     SimpleKey('target_filename', label="Target filename", default="filename.csv"),
                     SimpleKey('delimiter', default=";"),
                     #RepeatedKey('columns', 'column', content=SimpleKey('column'))]
                     RepeatedKey('columns', 'column',
                                 content=CompoundKey('column',
                                                     text_value='title',
                                                     attributes={'attribute': 'attribute',
                                                                 'renderer': 'renderer'},
                                                     fields=[InputField('title', label="Title",
                                                                        help_text="Column title in header"),
                                                             InputField('attribute', label="Attribute",
                                                                        help_text="Source object attribute"),
                                                             InputField('renderer', label="Renderer",
                                                                        help_text="Renderer eval (optionnal)")]))]
    
    _design_metadata_ = dict(default_width=300)
    
    def __init__(self, config_node, component_id):
        """Initialize a new CSVWriter
        @param config: SafeConfigParser
        @type config: SafeConfigParser instance

        @param process_name: The process name to use
        @type process_name: String
        """
        self.config_node = config_node
        self.id = component_id


        self.encoding = self.get_config_key('encoding')
        self.columns = self.get_config_key('columns')
        self.delimiter = self.get_config_key('delimiter')

        self.column_definitions = list()
        self.renderers = dict()
        
        self.__retrieve_columns_definition()

        csv.register_dialect('%s_dialect' % self.id, delimiter=self.delimiter,
                quoting=csv.QUOTE_ALL)

    def __retrieve_columns_definition(self):
        for column_def in self.columns:
            if column_def.get('attribute'):
                attr = column_def.get('attribute')
            else:
                attr = column_def.get('title')
            
            self.column_definitions.append((attr,
                                            column_def.get('title')))
                
            if column_def.get('renderer'):
                self.renderers[attr] = column_def.get('renderer')

    def __get_column_attributes(self):
        return [col_def[0] for col_def in self.column_definitions]

    def get_column_names(self):
        return [col_def[1] for col_def in self.column_definitions]
    
    def write(self, values, key, output_filename, target_filename):
        target_file = open(output_filename, 'wb+')

        csvengine = DictWriter(target_file,
                self.get_column_names(), dialect='%s_dialect' % self.id)
        
        firstrow = dict()
        for colname in self.get_column_names():
            firstrow[colname] = colname
        csvengine.writerow(firstrow)

        for data in values:
            adapted_data = CSVAddon(data, self.column_definitions,
                                    self.renderers, self.encoding)
            csvengine.writerow(adapted_data)
            del adapted_data
            yield True

        target_file.close()
        yield True
