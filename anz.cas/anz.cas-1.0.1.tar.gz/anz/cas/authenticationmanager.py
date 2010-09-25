
# zope
from zope.interface import implements

from anz.cas.interfaces import IAuthenticationManager
from anz.cas.authentication import Authentication
from anz.cas.exceptions import AuthenticationException

class AuthenticationManager( object ):
    ''' Default implementation of the AuthenticationManager.
    The AuthenticationManager follows the following algorithm:
    The manager loops through the array of AuthenticationHandlers searching for
    one that can attempt to determine the validity of the credentials. If it
    finds one, it tries that one. If that handler returns true, it continues
    on. If it returns false, it looks for another handler. If it throws an
    exception, it aborts the whole process and rethrows the exception.
    Next, it trys the handle to resolve credentials in order to create a
    Principal.
    
    '''
    
    implements( IAuthenticationManager )
    
    def __init__( self, handlers=[] ):
        ''' Construct an authentication manager.
        
        @param handlers
        The list of AuthenticationHandlers that know how to process the
        credentials provided.
        
        '''
        self.handlers = handlers
    
    def authenticate( self, credentials ):
        ''' See interfaces.IAuthenticationManager. '''
        for h in self.handlers:
            if h.supports(credentials) and h.authenticate(credentials):
                return Authentication( h.resolvePrincipal( credentials ) )
        else:
            raise AuthenticationException( 'Authenticate %s failure.' %
                                           credentials )
