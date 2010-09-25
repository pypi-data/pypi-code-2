
# zope
from zope.interface import implements

from anz.cas.interfaces import ICredentials

class UsernameCredentials( object ):
    ''' The Credentials respresents the user.
    
    '''
    
    implements( ICredentials )
    
    def __init__( self, username ):
        ''' Construct an user password credential object.
        
        @param username
        the user name(id) of user
        
        '''
        self.username = username
    
    def getUsername( self ):
        ''' Retrieve user name. '''
        return self.username
    
class HttpBasedServiceCredentials( object ):
    ''' The Credentials representing an HTTP-based service.
    HTTP-based services (such as web applications) are often represented by
    the URL entry point of the application.
    
    '''
    
    implements( ICredentials )
    
    def __init__( self, callbackUrl ):
        ''' Constructor that takes the URL of the HTTP-based service and
        creates the Credentials object.
        
        @param callbackUrl
        the URL representing the service
        
        '''
        self.callbackUrl = callbackUrl

    def getCallbackUrl( self ):
        ''' Retrieve the callbackUrl. '''
        return self.callbackUrl
