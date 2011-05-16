from zope.interface import Interface

class ISequenceGenerator(Interface):
    '''A sequence generator returns a sequence of integers
    It's meant to be thread/ZEO safe
    New sequences start with 1
    '''
    def setNextValue(next_number):
        '''Set the next number in the sequence'''

    def getNextValue():
        '''Consume and return next number in sequence'''
