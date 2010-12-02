from configparser import SafeConfigParser
from io import StringIO

from pywapa.AbstractParser import AbstractParser


class CfgParser(AbstractParser):

    extensions = ['cfg', 'ini', 'text/x-ini']

    def parse(self, file_content):
        return self._cfg_to_dic(file_content)

    def dump(self, content):
        cfg = SafeConfigParser()
        self._dic_to_cfg(cfg, content)
        io_string = StringIO()
        cfg.write(io_string)
        io_string.seek(0)
        return io_string.read()

    def _cfg_to_dic(self, file_content):
        cfg_parser = SafeConfigParser()
        io_string = StringIO(file_content)
        cfg_parser.readfp(io_string)

        dic = {}

        self._insert_tuples_dic(cfg_parser.items('DEFAULT'), dic)
        
        for section in cfg_parser.sections():
            explosed_section = section.split('.')
            current = dic
            for e_section in explosed_section:
                if not e_section in current:
                    current[e_section] = {}
                    current = current[e_section]
                elif hasattr(current[e_section], '__iter__'):
                    current = current[e_section]
            self._insert_tuples_dic(cfg_parser.items(section), current)
        return dic

    def _insert_tuples_dic(self, tuples, dictionary):
        for (key, value) in tuples:
            if value.startswith('[') and value.endswith(']'):
                value = value[1:-1].split(',')
            dictionary[key] = value
        return dictionary


    def _dic_to_cfg(self, cfg, dictionnary, section_name = None):
        for key in dictionnary.keys():
            element = dictionnary[key]
            if hasattr(element, 'keys'):
                if section_name != None:
                    new_section = '%s.%s' % (section_name, key)
                else:
                    new_section = str(key)
                self._dic_to_cfg(cfg, element, new_section)
            elif hasattr(element, '__iter__') and not isinstance(element, str):
                if section_name != None and not cfg.has_section(section_name):
                    cfg.add_section(section_name)
                cfg.set(section_name, key, '[%s]' % (','.join(map(str, element))))
            else :
                if section_name != None and not cfg.has_section(section_name):
                    cfg.add_section(section_name)
                cfg.set(section_name, key, str(element))