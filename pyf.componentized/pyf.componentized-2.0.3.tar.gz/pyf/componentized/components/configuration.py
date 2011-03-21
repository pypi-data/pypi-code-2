from pyf.componentized import ET
from ConfigParser import SafeConfigParser

import warnings

class ConfigurationException(Exception):
    pass

class DuplicateSectionError(ConfigurationException):
    pass

class UnknownSectionError(ConfigurationException):
    pass

class UnknownOptionError(ConfigurationException):
    pass

class Configuration(object):
    
    def __init__(self):
        self.__config = dict()
        warnings.warn("Call to deprecated class Configuration.",
                      category=DeprecationWarning)
    
    def read_xml_node(self, config_node):
        for section_element in config_node.getchildren():
            if section_element.tag == 'section':
                section_name = section_element.get('name', 'default')

            else:
                if not self.has_section('default'):
                    self.add_section('default')

                name = section_element.tag
                value = section_element.text

                self.set('default', name, value)

            for option in section_element.getchildren():
                name = option.tag
                value = option.text
                if option.tag == 'key':
                    name = option.get('name')
                
                if not self.has_section(section_name):
                    self.add_section(section_name)

                self.set(section_name, name, value)

    def read_config_file(self, filename):
        config = SafeConfigParser()
        config.read(filename)

        for section in config.sections():
            if not self.has_section(section):
                self.add_section(section)

            for option in config.options(section):
                value = config.get(section, option)
                self.set(section, option, value)

    def get_config_key(self, option):
        return self.get(None, option)

    def get(self, section, option):
        if section is None:
            section = 'default'
        if self.has_section(section):
            if self.has_option(section, option):
                result = self.__config[section][option]
            else:
                raise UnknownOptionError('Unknown option %s on section %s' % (option, section))

        else:
            raise UnknownSectionError('Unknown section %s' % section)

        return result

    def get_list(self, section, option, separator=','):
        return [value.strip() for value in self.get(section, option).split(separator)]

    def clean(self):
        self.__config.clear()

    def has_section(self, section):
        return self.__config.has_key(section)

    def set_config_key(self, option, value):
        self.set(None, option, value)

    def set(self, section, option, value):
        if section is None:
            section = 'default'
            if not self.has_section(section):
                self.add_section(section)

        if not self.has_section(section):
            raise UnknownSectionError('Unknown section %s' % section)
        
        self.__config[section][option] = value
       
    def sections(self):
        result = self.__config.keys()
        result.sort()
        return result

    def add_section(self, section):
        if not self.has_section(section):
            self.__config[section] = dict()
        else:
            raise DuplicateSectionError('Duplicate section %s' % section)

    def has_option(self, section, option):
        result = False
        if self.has_section(section):
            if self.__config[section].has_key(option):
                result = True
        else:
            raise UnknownSectionError('Unknown section %s' % section)

        return result

    def options(self, section):
        if self.has_section(section):
            result = self.__config[section].keys()
            result.sort()
            return result
        else:
            raise UnknownSectionError('Unknown section %s' % section)

    def items(self, section):
        result = list()
        for option in self.options(section):
            value = self.get(section, option)
            result.append((option, value))

        return result

    def to_xml(self):
        element = ET.Element('configuration')
        for section in self.sections():
            section_node = ET.SubElement(element, 'section')
            section_node.set('name', section)
            for option in self.options(section):
                option_node = ET.SubElement(section_node, 'key')
                option_node.set('name', option)
                option_node.text = self.get(section, option)

        return ET.tostring(element)
        
        









