# -*- coding: utf-8 -*-
'''
Attribute parser for C#.

@author: tzulberti
'''

from logging import getLogger

from pywebuml.initialize.parsers.base_typed.attribute_parser import AbstractStaticTypeAttributeParser

LOGGER = getLogger(__name__)


class CSharpAttributeParser(AbstractStaticTypeAttributeParser):
    ''' Attribute parser for C# classes.
    '''


    def clean_line(self, current_line):
        ''' Adds the option of removing the property definition
        of the line if there is any.
        '''
        res = super(CSharpAttributeParser, self).clean_line(current_line)
        if '{' in res:
            res = res[0:res.index('{')]
            res = res.strip()
        return res


    def should_skip_language_attributes(self, current_line):
        ''' Skip the attributes that indicates that the class can be
        indexed.
        '''
        return 'this' in current_line or 'this [' in current_line


    def get_referenced_class_complete_path(self, referenced_class, content):
        ''' Completes the name of the class using the global namespace.
        '''
        # TODO search the class in the database.
        return 'global.%s' % referenced_class
