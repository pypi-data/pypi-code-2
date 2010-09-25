
# python
from datetime import datetime

# zope
from Persistence import Persistent
from zope.interface import implements

from anz.cas.interfaces import IService
from anz.cas.utils import genUniqueId, sendMessageToEndPoint

class Service( Persistent ):
    ''' See interfaces.IService. '''
    
    implements( IService )
    
    def __init__( self, originalUrl, artifactId=None,
                  responseType=None, loggedOutAlready=False ):
        ''' Construct an service object.
        
        @param originalUrl
        The original url provided, used to reconstruct the redirect url.
        
        @param artifactId
        
        @param responseType
        
        @param loggedOutAlready
        indicator if the service has been sended logout request
        
        '''
        # get originalUrl as id
        self.id = originalUrl
        self.originalUrl = originalUrl
        self.artifactId = artifactId
        self.responseType = responseType
        self.loggedOutAlready = loggedOutAlready
        
        self.principal = None
    
    def getId( self ):
        ''' See interfaces.IService. '''
        return self.id
    
    def getPrincipal( self ):
        ''' See interfaces.IService. '''
        return self.principal
    
    def setPrincipal( self, principal ):
        ''' See interfaces.IService. '''
        self.principal = principal
    
    def matches( self, service ):
        ''' See interfaces.IService. '''
        return self.id == service.id
    
    def logOutOfService( self, sessionIdentifier ):
        ''' See interfaces.IService. '''
        if self.loggedOutAlready:
            return True
        
        self.loggedOutAlready = True
        
        lr = []
        lr.append( '<samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="%s" Version="2.0" IssueInstant="%s">' % \
                   (genUniqueId('LR'),datetime.utcnow()) )
        lr.append( '<saml:NameID xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">@NOT_USED@</saml:NameID>' )
        lr.append( '<samlp:SessionIndex>%s</samlp:SessionIndex>' % \
                   sessionIdentifier )
        lr.append( '</samlp:LogoutRequest>' )
        
        return sendMessageToEndPoint( self.originalUrl, ''.join(lr) )
