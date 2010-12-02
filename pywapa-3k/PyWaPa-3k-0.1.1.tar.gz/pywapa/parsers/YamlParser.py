from yaml import load, dump

from pywapa.AbstractParser import AbstractParser


class YamlParser(AbstractParser):

    extensions = ['yaml', 'yml', 'text/x-yaml']
    '''
    extensions accepted by JsonParser : [yaml, yml, text/x-yaml]
    '''

    def parse(self, file_content):
        return load(file_content)

    def dump(self, content):
        return dump(content, default_flow_style=False)

