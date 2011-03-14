# -*- coding: utf-8 -*-

'''
Created on 05/02/2011

@author: tzulberti
'''

from pywebuml.initialize.parsers.base_typed.method_parser import AbstractStaticTypeMethodParser


class CSharpMethodParser(AbstractStaticTypeMethodParser):
    ''' Parser for CSharp methods.
    '''

    def clean_language_things(self, signature):
        ''' Removes the templates conditions of the method signature.
        '''
        # TODO keyword bug
        if 'where' in signature and ':' in signature and signature.index('where') > signature.index(')'):
            # take into account methods that uses templates with conditionals.
            signature = signature[:signature.index('where')].strip()
        elif ':' in signature:
            # take into account that it cant be an inline constructor.
            # for example:
            #   public MyClass(): this("foo") {}
            signature = signature[:signature.index(':')].strip()
        return signature


    def should_skip_language_methods(self, signature):
        ''' Skip the method if it is an operator.
        '''
        return self.has_any_keyword(signature, ['operator'])

