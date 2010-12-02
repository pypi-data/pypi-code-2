from json import loads, dumps

from pywapa.AbstractParser import AbstractParser


class JsonParser(AbstractParser):

    extensions = ['json']
    '''
    extensions accepted by JsonParser : [json]
    '''

    def parse(self, file_content):
        return loads(file_content)

    def dump(self, content):
        return dumps(content, sort_keys=True, indent=4)

