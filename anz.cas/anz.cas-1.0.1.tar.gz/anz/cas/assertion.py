
# zope
from zope.interface import implements

from anz.cas.interfaces import IAssertion

class Assertion( object ):
    ''' See interfaces.IAssertion. '''
    
    implements( IAssertion )
    
    def __init__( self, service, authentications=[], fromNewLogin=False ):
        ''' Construct an assertion object.
        
        @param service
        The service we are asserting this ticket for
        
        @param authentications
        the chain of authentications
        
        @param fromNewLogin
        the service ticket from a new login
        
        '''
        self.service = service
        self.authentications = authentications
        self.fromNewLogin = fromNewLogin
    
    def getChainedAuthentications( self ):
        ''' See interfaces.IAssertion. '''
        return self.authentications
    
    def isFromNewLogin( self ):
        ''' See interfaces.IAssertion. '''
        return self.isFromNewLogin
    
    def getService( self ):
        ''' See interfaces.IAssertion. '''
        return self.service
