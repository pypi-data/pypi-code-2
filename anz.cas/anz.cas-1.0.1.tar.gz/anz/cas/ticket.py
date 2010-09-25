
# python
from datetime import datetime
from logging import getLogger

# zope
from Persistence import Persistent
from zope.interface import implements
from persistent.mapping import PersistentMapping

from anz.cas.interfaces import ITicket, ITicketGrantingTicket, IServiceTicket
from anz.cas.exceptions import InvalidTicketException

LOG = getLogger( 'anz.cas' )

class Ticket( Persistent ):
    ''' Base class of ticket.
    '''
    
    implements( ITicket )
    
    def __init__( self, id, tgt, policy=None ):
        ''' Construct a ticket.
        
        @param id
        the id of the Ticket
        
        @param tgt
        the TicketGrantingTicket parent
        
        @param policy
        the expiration policy for this ticket.
        
        '''
        self.id = id
        self.grantTgt = tgt
        self.created = datetime.utcnow()
        self.lastUsed = datetime.utcnow()
        self.countOfUses = 0
        self.expired = False
    
    def getId( self ):
        ''' See interfaces.ITicket. '''
        return self.id
    
    def getGrantingTicket( self ):
        ''' See interfaces.ITicket. '''
        return self.grantTgt
    
    def getCreationTime( self ):
        ''' See interfaces.ITicket. '''
        return self.created

    def getCountOfUses( self ):
        ''' See interfaces.ITicket. '''
        return self.countOfUses
    
    def expire( self ):
        ''' See interfaces.ITicket. '''
        self.expired = True

    def isExpired( self ):
        ''' See interfaces.ITicket. '''
        return self.expired == True
    
    def updateState( self ):
        self.lastUsed = datetime.utcnow()
        self.countOfUses += 1

class TicketGrantingTicket( Ticket ):
    ''' A TicketGrantingTicket is the global identifier of a principal into
    the system. It grants the Principal single-sign on access to any service
    that opts into single-sign on.
    
    Expiration of a TicketGrantingTicket is controlled by the ExpirationPolicy
    specified as object creation.
    
    '''
    
    implements( ITicketGrantingTicket )
    
    PREFIX = 'TGT'
    
    def __init__( self, id, tgt, authentication ):
        ''' Construct a ticket granting ticket.
        
        @param id
        the id of the Ticket
        
        @param tgt
        the parent ticket granting ticket
        
        @param authentication
        the Authentication request for this ticket
        
        '''
        super(TicketGrantingTicket, self).__init__( id, tgt )
        
        self.authentication = authentication
        self.services = PersistentMapping()
    
    def getAuthentication( self ):
        ''' See interfaces.ITicketGrantingTicket. '''
        return self.authentication
    
    def grantServiceTicket( self, id, service, credentialsProvided ):
        ''' See interfaces.ITicketGrantingTicket. '''
        st = ServiceTicket( id, self, service,
                            self.getCountOfUses()==0 or credentialsProvided )
        
        self.updateState()
        
        # binding principal to service
        authentications = self.getChainedAuthentications()
        service.setPrincipal( authentications[-1].getPrincipal() )
        
        self.services[id] = service
        return st
    
    def getChainedAuthentications( self ):
        ''' See interfaces.ITicketGrantingTicket. '''
        ret = []
        ret.append( self.getAuthentication() )
        
        # iterate tgt chain
        parent = self.getGrantingTicket()
        while parent:
            ret.append( parent.getAuthentication() )
            parent = parent.getGrantingTicket()
        
        return ret
    
    def expire( self ):
        ''' See interfaces.ITicket. '''
        super(TicketGrantingTicket, self).expire()
        
        # logout services
        for key in self.services.keys():
            service = self.services[key]
            if not service.logOutOfService( key ):
                LOG.warning( 'Logout message not sent to [' + service.getId() + \
                             ']; Continuing processing...' )

class ServiceTicket( Ticket ):
    ''' A service ticket is used to grant access to a specific service for a
    principal. A Service Ticket is generally a one-time use ticket.
    
    '''
    
    implements( IServiceTicket )
    
    PREFIX = 'ST'
    
    def __init__( self, id, tgt, service, fromNewLogin ):
        ''' Construct a service ticket.
        
        @param id
        the id of the Ticket
        
        @param tgt
        the TicketGrantingTicket parent
        
        @param service
        the service this ticket is for
        
        @param fromNewLogin
        is it from a new login
        
        '''
        super(ServiceTicket, self).__init__( id, tgt )
        
        self.service = service
        self.fromNewLogin = fromNewLogin
        self.grantedTicketAlready = False
    
    def getService( self ):
        ''' See interfaces.IServiceTicket. '''
        return self.service
    
    def isFromNewLogin( self ):
        ''' See interfaces.IServiceTicket. '''
        return self.fromNewLogin
    
    def isValidFor( self, serviceToValidate ):
        ''' See interfaces.IServiceTicket. '''
        self.updateState()
        return serviceToValidate.matches( self.service )
    
    def grantTicketGrantingTicket( self, id, authentication ):
        ''' See interfaces.IServiceTicket. '''
        if self.grantedTicketAlready:
            raise InvalidTicketException(
                'Tgt already generated for St %s.' % self.id )
        
        self.grantedTicketAlready = True
        return TicketGrantingTicket( id, self.getGrantingTicket(),
                                     authentication )
