#! -*- coding: UTF-8 -*-
from zope.interface import Interface

class INumberator(Interface):
    ''' Interface to generate number, like postgres sequence'''

    def number_it(content):
        ''' Return the next number and update the last_number
        and save a number-> UID map'''

    def get_current():
        '''  Return the last_number '''

    def get_UID(number):
        ''' Return the UID of content from the number'''

class INumbered(Interface):
    ''' Interface to be used in the objects to set and get a incremental number to it
    based on the INumberator '''
    
    def get_number():
        ''' Get the number for the object, if it don't have a number will be created and returned '''

class IInscricoes(Interface):
    """ Um folder para inscricoes
    """