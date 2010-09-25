
# zope
from Persistence import Persistent
from zope.interface import implements

from anz.cas.interfaces import IPrincipal

class Principal( Persistent ):
    ''' See interfaces.IPrincipal. '''
    
    implements( IPrincipal )
    
    def __init__( self, id ):
        ''' Construct an principal object.
        
        @param id
        the id of principal
        
        '''
        self.id = id
    
    def getId( self ):
        ''' See interfaces.IPrincipal. '''
        return self.id
