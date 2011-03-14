# -*- coding: utf-8 -*-

'''
Attribute parser for Java files.

@author: tzulberti
Created on: 13/03/2010
'''

from pywebuml.initialize.parsers.base_typed.attribute_parser import AbstractStaticTypeAttributeParser

class JavaAttributeParser(AbstractStaticTypeAttributeParser):
    ''' Java attribute parser for the java classes.
    '''

    def get_referenced_class_complete_path(self, referenced_class, content):
        ''' Checks the import of the content to find the referenced class.

        If it is found, then it returns that path, if that isn't the case,
        it will return the name of the referenced_class.

        :see:
            AbstractStaticTypeAttributeParser.get_referenced_class_complete_path
        '''
        for line in content:
            if self.has_any_keyword(line, ['import']) and \
                    line.endswith(referenced_class + ";") :
                res = self.remove_keywords(line, ['import'])
                res = res.replace(';', '')
                res = res.strip()
                return res

        # if no import was found, then it must be in the same package
        # that the current file.
        for line in content:
            if self.has_any_keyword(line, ['package']):
                package = self.remove_keywords(line, ['package'])
                package = package.replace(';', '')
                package = package.strip()
                return '%s.%s' % (package, referenced_class)

        # if there is no import and package then the java file is in the
        # default path
        return referenced_class
