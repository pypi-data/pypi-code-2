
# python
from datetime import datetime

# zope
from Persistence import Persistent
from zope.interface import implements

from anz.cas.interfaces import IAuthentication

class Authentication( Persistent ):
    ''' See interfaces.IAuthentication. '''
    
    implements( IAuthentication )
    
    def __init__( self, principal ):
        ''' Construct an authentication object.
        
        @param principal
        the principal
        
        '''
        self.principal = principal
        self.created = datetime.utcnow()
    
    def getPrincipal( self ):
        ''' See interfaces.IAuthentication. '''
        return self.principal
    
    def getAuthenticatedDate( self ):
        ''' See interfaces.IAuthentication. '''
        return self.created
