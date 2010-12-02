
class ParserError(Exception):
    '''
    Base exception for parsing and dumping.
    '''
    pass

class AbstractParser(object):
    '''
    Base class for Parsers.
    '''

    extensions = []
    '''List of extensions supported by parser.'''

    def __init__(self):
        pass

    def parse(self, file_content):
        '''
        Return parse of file_content.
        
        Arguments :
         * file_content : string
        '''
        raise NotImplementedError

    def dump(self, content):
        '''
        Return dump of content.
        
        Arguments :
         * content : string
        '''
        raise NotImplementedError