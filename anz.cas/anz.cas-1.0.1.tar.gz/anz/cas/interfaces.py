
# zope
from zope.interface import Interface

class IAnzCentralAuthService( Interface ):
    '''
    '''
    
    def login( service=None, renew=None, gateway=None ):
        ''' Called by user to login CAS.
        
        It responds to credentials by acting as a credential requestor, any
        PAS authentication plugin will act as a credential acceptor.
        
        @param service
        The identifier of the application the client is trying to access.
        Usually this is a service url, this url act as a callback url,
        when user authentication successfully, redirect browser to this url.
        If a service is not specified and a single sign-on session does not
        yet exist, CAS SHOULD request credentials from the user to initiate
        a single sign-on session. If a service is not specified and a single
        sign-on session already exists, CAS SHOULD display a message notifying
        the client that it is already logged in.
        
        @param renew
        If this parameter is set, single sign-on will be bypassed. In this
        case, CAS will require the client to present credentials regardless
        of the existence of a single sign-on session with CAS. This parameter
        is not compatible with the "gateway" parameter. Services redirecting
        to the /login URI and login form views posting to the /login URI SHOULD
        NOT set both the "renew" and "gateway" request parameters. CAS will
        ignore the "gateway" parameter if "renew" is set. It is RECOMMENDED
        that when the renew parameter is set its value be "true".
        
        @param gateway
        If the client has a pre-existing single sign-on session with CAS, or
        if a single sign-on session can be established through non-interactive
        means (i.e. trust authentication), CAS MAY redirect the client to the
        URL specified by the "service" parameter, appending a valid service
        ticket. If the client does not have a single sign-on session with CAS,
        and a non-interactive authentication cannot be established, CAS MUST
        redirect the client to the URL specified by the "service" parameter
        with no "ticket" parameter appended to the URL. If the "service"
        parameter is not specified and "gateway" is set, CAS request credentials
        as if neither parameter was specified. This parameter is not compatible
        with the "renew" parameter. If both are set, it act as if "gateway" is
        not set. It is RECOMMENDED that when the gateway parameter is set its
        value be "true".
        
        @return
        One of the following responses MUST be provided by /login:
        
        * successful login: redirect the client to the URL specified by the
        "service" parameter in a manner that will not cause the client's
        credentials to be forwarded to the service. This redirection MUST
        result in the client issuing a GET request to the service. The request
        MUST include a valid service ticket, passed as the HTTP request
        parameter, "ticket". If "service" was not specified, CAS MUST display
        a message notifying the client that it has successfully initiated a
        single sign-on session.
        
        * failed login: return to /login as a credential requestor. It is
        RECOMMENDED in this case that the CAS server display an error message
        be displayed to the user describing why login failed (e.g. bad
        password, locked account, etc.), and if appropriate, provide an
        opportunity for the user to attempt to login again.
        
        '''
    
    def logout( url=None ):
        ''' Called by user to logout CAS.
        
        It destroys a client's single sign-on CAS session. The ticket-granting
        cookie is destroyed, and subsequent requests to /login will not obtain
        service tickets until the user again presents primary credentials (and
        thereby establishes a new single sign-on session)
        
        @param url
        URL of the service the user logged out from.
        
        @return
        Display a page stating that the user has been logged out. If the "url"
        request parameter is provided, a link to the provided URL is shown.
        
        '''
    
    def validate( service, ticket, renew=None ):
        ''' Checks the validity of a service ticket [CAS 1.0].
        
        /validate is part of the CAS 1.0 protocol and thus does not handle
        proxy authentication. CAS MUST respond with a ticket validation failure
        response when a proxy ticket is passed to /validate.
        
        @param service
        usually this is a service url, this url act as a callback url,
        when user authentication successfully, redirect browser to this url.
        
        @param ticket
        the service ticket issued by /login
        
        @param renew
        if this parameter is set, ticket validation will only succeed if the
        service ticket was issued from the presentation of the user's primary
        credentials. It will fail if the ticket was issued from a single
        sign-on session. It is RECOMMENDED that when the renew parameter is
        set its value be "true".
        
        @return
        On ticket validation success:
        yes<LF>
        username<LF>
        
        On ticket validation failure:
        no<LF>
        <LF>
        
        '''
    
    def serviceValidate( service, ticket, pgtUrl=None, renew=None ):
        ''' Checks the validity of a service ticket and returns an XML-fragment
        response [CAS 2.0].
        
        /serviceValidate MUST also generate and issue proxy-granting tickets
        when requested. /serviceValidate MUST NOT return a successful
        authentication if it receives a proxy ticket. It is RECOMMENDED that
        if /serviceValidate receives a proxy ticket, the error message in the
        XML response SHOULD explain that validation failed because a proxy
        ticket was passed to /serviceValidate.
        
        @param service
        the identifier of the service for which the ticket was issued
        
        @param ticket
        the service ticket issued by /login
        
        @param pgtUrl
        the URL of the proxy callback
        
        @param renew
        if this parameter is set, ticket validation will only succeed if the
        service ticket was issued from the presentation of the user's primary
        credentials. It will fail if the ticket was issued from a single
        sign-on session. It is RECOMMENDED that when the renew parameter is
        set its value be "true".
        
        @return
        an XML-formatted CAS serviceResponse:
        
        On ticket validation success:
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationSuccess>
                <cas:user>username</cas:user>
                <cas:proxyGrantingTicket>PGTIOU-84678-8a9d...</cas:proxyGrantingTicket>
            </cas:authenticationSuccess>
        </cas:serviceResponse>
        
        On ticket validation failure:
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationFailure code="INVALID_TICKET">
                Ticket ST-1856339-aA5Yuvrxzpv8Tau1cYQ7 not recognized
            </cas:authenticationFailure>
        </cas:serviceResponse>
        
        '''
    
    def proxyValidate( service, ticket, pgtUrl=None, renew=None ):
        ''' Perform the same validation tasks as /serviceValidate and
        additionally validate proxy tickets [CAS 2.0].
        
        MUST be capable of validating both service tickets and proxy tickets.
        
        @param service
        the identifier of the service for which the ticket was issued
        
        @param ticket
        the proxy ticket issued by /proxy
        
        @param pgtUrl
        the URL of the proxy callback
        
        @param renew
        if this parameter is set, ticket validation will only succeed if the
        service ticket was issued from the presentation of the user's primary
        credentials. It will fail if the ticket was issued from a single
        sign-on session. It is RECOMMENDED that when the renew parameter is
        set its value be "true".
        
        @return
        an XML-formatted CAS serviceResponse.
        
        On ticket validation success:
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationSuccess>
                <cas:user>username</cas:user>
                <cas:proxyGrantingTicket>PGTIOU-84678-8a9d...</cas:proxyGrantingTicket>
                <cas:proxies>
                    <cas:proxy>https://proxy2/pgtUrl</cas:proxy>
                    <cas:proxy>https://proxy1/pgtUrl</cas:proxy>
                </cas:proxies>
            </cas:authenticationSuccess>
        </cas:serviceResponse>
        
        On ticket validation failure:
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:authenticationFailure code="INVALID_TICKET">
                ticket PT-1856376-1HMgO86Z2ZKeByc5XdYD not recognized
            </cas:authenticationFailure>
        </cas:serviceResponse>
        
        '''
    
    def proxy( pgt, targetService ):
        ''' Provides proxy tickets to services that have acquired
        proxy-granting tickets and will be proxying authentication to
        back-end services [CAS 2.0].
        
        @param pgt
        the proxy-granting ticket acquired by the service during service
        ticket or proxy ticket validation
        
        @param targetService
        the service identifier of the back-end service.
        Note that not all back-end services are web services so this service
        identifier will not always be a URL. However, the service identifier
        specified here MUST match the "service" parameter specified to
        /proxyValidate upon validation of the proxy ticket.
        
        @return
        an XML-formatted CAS serviceResponse.
        
        On request success:
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:proxySuccess>
                <cas:proxyTicket>
                    PT-1856392-b98xZrQN4p90ASrw96c8
                </cas:proxyTicket>
            </cas:proxySuccess>
        </cas:serviceResponse>        
        
        On request failure:
        <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            <cas:proxyFailure code="INVALID_REQUEST">
                'pgt' and 'targetService' parameters are both required
            </cas:proxyFailure>
        </cas:serviceResponse>
        
        '''

class ICredentials( Interface ):
    ''' Marker interface for credentials required to authenticate a principal.
    
    The Credentials is an opaque object that represents the information a user
    asserts proves that the user is who it says it is. In CAS, any information
    that is to be presented for authentication must be wrapped (or implement)
    the Credentials interface.
    Credentials can contain a userid and password, or a Certificate, or an IP
    address, or a cookie value. Some credentials require validation, while
    others are inherently trustworthy.
    
    Credentials objects that are included in CAS do NOT expose any confidential
    information.
    
    '''
    pass

class IPrincipal( Interface ):
    ''' Generic concept of an authenticated thing. Examples include a person or
    a service.
    
    '''
    
    def getId():
        ''' Returns the unique id for the Principal.
        
        @return
        the unique id for the Principal
        
        '''

class IService( IPrincipal ):
    ''' Marker interface for Service.
    Services are generally either remote applications utilizing CAS or
    applications that principals wish to gain access to. In most cases
    this will be some form of web application.
    
    '''
    
    def getPrincipal():
        ''' Retrieve principal this service grant to. '''
    
    def setPrincipal( principal ):
        ''' Set principal this service grant to.
        '''
    
    def matches( service ):
        ''' '''
    
    def getResponse( ticketId ):
        ''' Constructs the url to redirect the service back to.
        
        @param ticketId
        the service ticket to provide to the service.
        
        @return
        the redirect url.
        
        '''
    
    def getArtifactId():
        ''' Retrieves the artifact supplied with the service. May be null.
        
        @return
        the artifact if it exists, null otherwise.
        
        '''
    
    def logOutOfService( sessionIdentifier ):
        ''' Logout current service when do single sign out.
        
        @param sessionIdentifier
        session id used to find according session in CAS-client service.
        
        '''

class IAuthentication( Interface ):
    ''' Interface of an authentication object.
    The Authentication object represents a successful authentication request.
    It contains the principal that the authentication request was made for as
    well as the additional meta information such as the authenticated date.
    
    An Authentication object must be serializable to permit persistance and
    clustering.
    
    '''

    def getPrincipal():
        ''' Retrieve the principal.
        
        @return
        a Principal implementation
        
        '''
    
    def getAuthenticatedDate():
        ''' Retrieve the time of when this Authentication object was created.
        
        @return
        the date/time the authentication occurred
        
        '''

class IAssertion( Interface ):
    ''' Interface of Assertion object.
    Assertion object provided by the CAS server, contains validation
    information, the most important is a chain of Principal objects.
    The first is the User's login Principal, while any others are
    Proxy Principals.
    
    '''

    def getChainedAuthentications():
        ''' Get a List of Authentications which represent the owners of the
        GrantingTickets which granted the ticket that was validated. The first
        Authentication of this list is the Authentication which originally
        authenticated to CAS to obtain the first Granting Ticket. Subsequent
        Authentication are those associated with GrantingTickets that were
        granted from that original granting ticket. The last Authentication in
        this List is that associated with the GrantingTicket that was the
        immediate grantor of the ticket that was validated. The List returned
        by this method will contain at least one Authentication.
        
        @return
        a List of Authentication
        
        '''
    
    def isFromNewLogin():
        ''' True if the validated ticket was granted in the same transaction as
        that in which its grantor GrantingTicket was originally issued.
        
        @return
        true if validated ticket was granted simultaneous with its grantor's
        issuance
        
        '''
    
    def getService():
        ''' Obtain the service this ticket is valid for.
        
        @return
        the service for which we are asserting this ticket is valid for.
        
        '''

class IValidationSpecification( Interface ):
    ''' An interface to impose restrictions and requirements on validations.
    '''
    
    def isSatisfiedBy( assertion ):
        ''' ???
        
        @param assertion
        The assertion we want to confirm is satisfied by this specification.
        
        '''

class IAuthenticationManager( Interface ):
    ''' Interface of Authentication Manager.
    The AuthenticationManager is the entity that determines the authenticity
    of the credentials provided. It (or a class it delegates to) is the sole
    authority on whether credentials are valid or not.
 
    '''
    
    def authenticate( credentials ):
        ''' Method to validate the credentials provided.
        On successful validation, a fully populated Authentication object will
        be returned. Typically this will involve resolving a principal and
        providing any additional attributes, but specifics are left to the
        individual implementations to determine. Failure to authenticate is
        considered an exceptional case, and an AuthenticationException is thrown.
        
        @param credentials
        The credentials to validate.
        
        @return
        If success a fully populated Authentication object returned, or an
        AuthenticationException object.
        
        '''

class IAuthenticationHandler( Interface ):
    ''' Validate Credentials support for Authentication Manager.
    Determines that Credentials are valid. Password-based credentials may be
    tested against an external LDAP, Kerberos, JDBC source. Certificates may
    be checked against a list of CA's and do the usual chain validation.
    
    Callers to this class should first call supports to determine if the
    AuthenticationHandler can authenticate the credentials provided.
    
    '''
    
    def authenticate( credentials ):
        ''' Method to determine if the credentials supplied are valid.
        
        @param credentials
        The credentials to validate.
        
        @return
        true if valid, return false otherwise.
        
        '''
    
    def supports( credentials ):
        ''' Method to check if the handler knows how to handle the credentials
        provided.
        
        @param credentials
        The credentials to check.
        
        @return
        true if the handler supports the Credentials, false othewrise.
        
        '''
    
    def resolvePrincipal( credentials ):
        ''' Turn Credentials into a Principal object by analyzing the
        information provided in the Credentials and constructing a Principal
        object based on that information.
        
        @param credentials
        The credentials to resolve.
        
        @return
        Resolved Principal, or None if the principal could not be resolved.
        
        '''

class IProxyHandler( Interface ):
    ''' Abstraction for what needs to be done to handle proxies.    
    
    '''
    
    def handle( credentials, pgtId ):
        ''' Method to actually process the proxy request.
        
        @param credentials
        The credentials of the item that will be proxying.
        
        @param pgtId
        The ticketId for the ProxyGrantingTicket
        
        @return
        The String value that needs to be passed to the CAS client.
        
        '''

class IServicesManager( Interface ):
    ''' Manages the storage, retrieval, and matching of Services wishing to
    use CAS and services that have been registered with CAS.
    
    '''
    
    def addService( id, name='', description='',
                    enabled=True, ssoEnabled=True,
                    anonymousAccess=False, allowedToProxy=True ):
        ''' Register a service with CAS.
        
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
        whether the service is allowed anonymous or priveleged access to
        user information.
     
        @param allowedToProxy
        Is this application allowed to take part in the proxying capabilities
        of CAS?
        
        '''
    
    def editService( id, name, description,
                     enabled, ssoEnabled,
                     anonymousAccess, allowedToProxy ):
        ''' Update an existing service.
        
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
        whether the service is allowed anonymous or priveleged access to
        user information.
     
        @param allowedToProxy
        Is this application allowed to take part in the proxying capabilities
        of CAS?
        
        '''
    
    def deleteService( id ):
        ''' Delete the entry for this RegisteredService.
        
        @param id
        the id of the registeredService to delete.
        
        @return
        the registered service that was deleted, None if there was none.
        
        '''
    
    def findServiceBy( service ):
        ''' Find a RegisteredService by matching with the supplied service.
        
        @param service
        the service to match with.
        
        @return
        the RegisteredService that matches the supplied service.
        
        '''
    
    def findServiceById( id ):
        ''' Find a RegisteredService by matching with the supplied id.
        
        @param id
        the id to match with.
        
        @return
        the RegisteredService that matches the supplied service.
        
        '''
    
    def getAllServices():
        ''' Retrieve the collection of all registered services.
        
        @return
        the collection of all services.
        
        '''

class IRegisteredService( Interface ):
    ''' Interface for a service that can be registered by the Services
    Management interface.
    
    '''
    
    def getId():
        ''' Return the unique identifier for this service.
        
        @return
        the unique identifier for this service.
        
        '''
    
    def getName():
        ''' Return name of the service.
        
        @return
        name of the service
        
        '''
    
    def getDescription():
        ''' Return the description of the service.
        
        @return
        the description of the service.
        
        '''
    
    def isEnabled():
        ''' Is this application currently allowed to use CAS?
        
        @return
        true if it can use CAS, false otherwise.
        
        '''
    
    def isSsoEnabled():
        ''' Does this application participate in the SSO session?
        
        @return
        true if it does, false otherwise.
        
        '''
    
    def isAnonymousAccess():
        ''' Determines whether the service is allowed anonymous or priveleged
        access to user information. Anonymous access should not return any
        identifying information such as user id.
        
        '''
    
    def isAllowedToProxy():
        ''' Is this application allowed to take part in the proxying
        capabilities of CAS?
        
        @return
        true if it can, false otherwise.
        
        '''
    
    def matches( service ):
        ''' Returns whether the service matches the registered service.
        
        @param service
        the service to match.
        
        @return
        true if they match, false otherwise.
        
        '''

class ITicket( Interface ):
    ''' Interface for the generic concept of a ticket. '''
    
    def getId():
        ''' Retrieve the ticket id.
        
        @return
        the id
        
        '''
    
    def isExpired():
        ''' Determines if the ticket is expired.
        
        @return
        True if expired, False not expired
        
        '''
    
    def getGrantingTicket():
        ''' Retrive the TicketGrantingTicket that granted this ticket.
        
        @return
        the ticket or null if it has no parent
        
        '''
    
    def getCreationTime():
        ''' Return the time the Ticket was created.
        
        @return
        the time the ticket was created.
        
        '''
    
    def getCountOfUses():
        ''' Returns the number of times this ticket was used.
        
        @return
        the number of times this ticket was used
        
        '''
    
    def expire():
        ''' Explicitly expire a ticket.
        This method will log out of any service associated with the Ticket
        Granting Ticket.
        
        '''

class ITicketGrantingTicket( ITicket ):
    ''' Interface for a ticket granting ticket. A TicketGrantingTicket is the
    main access into the CAS service layer. Without a TicketGrantingTicket, a
    user of CAS cannot do anything.
    
    '''
    
    def getAuthentication():
        ''' Retrieve the authenticated object for which this ticket was
        generated for.
        
        @return
        the authentication
        
        '''
    
    def grantServiceTicket( id, service, credentialsProvided ):
        ''' Grant a ServiceTicket for a specific service.
        
        @param id
        The unique identifier for this ticket
        
        @param service
        The service for which we are granting a ticket
        
        @param credentialsProvided
        
        
        @return
        the service ticket granted to a specific service for the
        principal of the TicketGrantingTicket
        
        '''
    
    def getChainedAuthentications():
        ''' Retrieve the chained list of Authentications for this
        TicketGrantingTicket.
        
        @return
        the list of principals
        
        '''

class IServiceTicket( ITicket ):
    ''' Interface for a Service Ticket. A service ticket is used to grant
    access to a specific service for a principal. A Service Ticket is generally
    a one-time use ticket.
    
    '''
    
    def getService():
        ''' Retrieve the service this ticket was given for.
        
        @return
        the server.
        
        '''
    
    def isFromNewLogin():
        ''' Determine if this ticket was created at the same time as a
        TicketGrantingTicket.
        
        @return
        true if it is, false otherwise.
        
        '''
    
    def isValidFor( serviceToValidate ):
        '''
        '''
    
    def grantTicketGrantingTicket( id, authentication ):
        ''' Grant a TicketGrantingTicket from this service to the
        authentication.
        
        @param id
        The unique identifier for this ticket
        
        @param authentication
        The Authentication we wish to grant a ticket for. Maybe a user or a
        proxy app.
        
        @return
        The ticket granting ticket.
        
        '''
    
    