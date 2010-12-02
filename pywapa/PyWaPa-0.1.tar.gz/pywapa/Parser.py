from pywapa.AbstractParser import AbstractParser

import pywapa.parsers.XmlParser
import pywapa.parsers.JsonParser
import pywapa.parsers.CfgParser
import pywapa.parsers.YamlParser

class NoDeclaredParser(Exception):
    pass

class NoCompatibleParser(Exception):
    pass

class MultipleCompatibleParsers(Exception):
    pass

class Parser(object):
    '''
    Main class.
    '''

    def __init__(self, markup):
        '''
        Constructor, take 2 arguments :
        
         * markup : markup used to parser/dump (str)
        '''
        self.__markup = markup
        self.__parser_instance = self.parser_from_markup(self.__markup)()

    def parser_from_markup(self, markup):
        '''
        Search for Parser corresponding to markup indicator and return Parser.
        If no Parser is available, raise an Exception.
        If no Parser is able to parse/dump, an Exception is raises.
        
        Arguments :
         * markup : markup indicator (str)
         
        Return :
        
            Parser class corresponding of markup indicator.
        '''
        parsers = AbstractParser.__subclasses__()
        if len(parsers) == 0:
            raise NoDeclaredParser
        compatibles_parsers = [parser for parser in parsers if markup in parser.extensions]
        if len(compatibles_parsers) == 0:
            raise NoCompatibleParser
        elif len(compatibles_parsers) > 1:
            raise MultipleCompatibleParsers
        return compatibles_parsers[0]

    def parse(self, content):
        '''
        Return parsed content.

        Arguments :
         * content -- string to be dumped
        '''
        result = self.__parser_instance.parse(content)
        return result

    def dump(self, content):
        '''
        Return dumped content in markup.
        
        Arguments :        
         * content -- string to be dumped
        '''
        return self.__parser_instance.dump(content)