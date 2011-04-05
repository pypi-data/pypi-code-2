# -*- coding: utf-8 -*-

'''
@author: tzulberti
Created on 13/03/2010
'''

from pywebuml.initialize.parsers.base_typed.method_parser import AbstractStaticTypeMethodParser
from pywebuml.initialize.parsers.constants import JAVA_LANGUAGE_METHODS

class JavaMethodParser(AbstractStaticTypeMethodParser):
    ''' Parser for java methods.
    '''

    def clean_language_things(self, signature):
        ''' Doesn't changes the signature.
        '''
        return signature

    def should_skip_language_methods(self, signature):
        ''' Skip all the methods that belong to the Java Object methods.
        '''
        return self.has_any_keyword(signature, JAVA_LANGUAGE_METHODS)
