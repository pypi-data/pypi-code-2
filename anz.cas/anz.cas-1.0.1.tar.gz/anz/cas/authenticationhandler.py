
# zope
from zope.interface import implements

from anz.cas.interfaces import IAuthenticationHandler
from anz.cas.credentials import UsernameCredentials, HttpBasedServiceCredentials
from anz.cas.principal import Principal
from anz.cas.service import Service
from anz.cas.utils import isValidEndPoint

class UsernameCredentialAuthenticationHandler( object ):
    ''' UsernameCredentials respresents the username that a user may provide in
    order to prove the authenticity of who they say they are.
    
    '''
    
    implements( IAuthenticationHandler )
    
    def authenticate( self, credentials ):
        ''' Authentication has been done by PAS auth plugin, so here we just
        return True.
        '''
        return True
    
    def supports( self, credentials ):
        ''' See interfaces.IAuthenticationHandler. '''
        return credentials and isinstance( credentials,
                                           UsernameCredentials )
    
    def resolvePrincipal( self, credentials ):
        ''' See interfaces.IAuthenticationHandler. '''
        return Principal( credentials.getUsername() )

class HttpBasedServiceCredentialsAuthenticationHandler( object ):
    ''' Class to validate the credentials presented by communicating with the
    web server and checking the certificate that is returned against the
    hostname, etc.
    This class is concerned with ensuring that the protocol is HTTPS and that a
    response is returned. The SSL handshake that occurs automatically by
    opening a connection does the heavy process of authenticating.
 
    '''
    
    implements( IAuthenticationHandler )

    # The string representing the HTTPS protocol
    PROTOCOL = 'https'
    
    def __init__( self, requireSecure=True ):
        ''' Construct an authentication manager.
        
        @param requireSecure
        whether secure connection is required or not
        
        '''
        self.requireSecure = requireSecure
    
    def authenticate( self, credentials ):
        ''' See interfaces.IAuthenticationHandler. '''
        if self.requireSecure and \
           credentials.getCallbackUrl().find(self.PROTOCOL)!=0:
            return False
        
        return isValidEndPoint( credentials.getCallbackUrl() )
    
    def supports( self, credentials ):
        ''' See interfaces.IAuthenticationHandler. '''
        return credentials and isinstance( credentials,
                                           HttpBasedServiceCredentials )
    
    def resolvePrincipal( self, credentials ):
        ''' See interfaces.IAuthenticationHandler. '''
        return Service( credentials.getCallbackUrl() )
