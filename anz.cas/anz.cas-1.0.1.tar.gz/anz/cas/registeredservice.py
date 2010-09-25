
# zope
from zope.interface import implements
from Persistence import Persistent

from anz.cas.interfaces import IRegisteredService

class RegisteredService( Persistent ):
    ''' A service that can be registered by the Services Management. '''
    
    implements( IRegisteredService )
    
    def __init__( self, id, name='', description='',
                  enabled=True, ssoEnabled=True,
                  anonymousAccess=False, allowedToProxy=True ):
        ''' Construct a registered service object.
        
        @param id
        the unique identifier for this service, usually use root url of the
        service as it.
        
        @param name
        name of this service
        
        @param description
        description of this service
        
        @param enabled
        Is this application currently allowed to use CAS?
        
        @param ssoEnabled
        Does this application participate in the SSO session?
        
        @param anonymousAccess
        whether the service is allowed anonymous or privileged access to
        user information.
     
        @param allowedToProxy
        Is this application allowed to take part in the proxying capabilities
        of CAS?
        
        '''
        self.id = id
        self.name = name
        self.description = description
        self.enabled = enabled
        self.ssoEnabled = ssoEnabled
        self.anonymousAccess = anonymousAccess
        self.allowedToProxy = allowedToProxy
        
    def getId( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.id
    
    def getName( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.name
    
    def getDescription( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.description
    
    def isEnabled( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.enabled
    
    def isSsoEnabled( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.ssoEnabled
    
    def isAnonymousAccess( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.anonymousAccess
    
    def isAllowedToProxy( self ):
        ''' See interfaces.IRegisteredService. '''
        return self.allowedToProxy
    
    def matches( self, service ):
        ''' See interfaces.IRegisteredService. '''
        return service and service.getId().lower().find(self.id.lower())==0
