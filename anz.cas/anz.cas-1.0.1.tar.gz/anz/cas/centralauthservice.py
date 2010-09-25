
# python
from datetime import timedelta
from urllib import quote, unquote
from logging import getLogger
from xml.sax.saxutils import escape
from copy import deepcopy

# zope
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from BTrees.OOBTree import OOBTree

from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.bforest import utils
from zope.bforest.periodic import OOBForest

# cmf
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.CMFCore.permissions import ManagePortal, View

from anz.cas.interfaces import IAnzCentralAuthService, IServicesManager
from anz.cas.credentials import UsernameCredentials, HttpBasedServiceCredentials
from anz.cas.ticket import TicketGrantingTicket, ServiceTicket
from anz.cas.service import Service
from anz.cas.exceptions import BaseException, InvalidRequestException, \
     InvalidTicketException, ServiceValidationException, \
     UnauthorizedServiceException, UnauthorizedSsoServiceException, \
     UnauthorizedProxyingException, AuthenticationException
from anz.cas.authenticationmanager import AuthenticationManager
from anz.cas.authenticationhandler import \
     UsernameCredentialAuthenticationHandler, \
     HttpBasedServiceCredentialsAuthenticationHandler
from anz.cas.assertion import Assertion
from anz.cas.registeredservice import RegisteredService
from anz.cas.proxyhandler import ProxyHandler
from anz.cas.validationspecification import CAS10ValidationSpecification, \
     CAS20ValidationSpecification, CAS20WithoutProxyingValidationSpecification
from anz.cas.utils import genUniqueId

LOG = getLogger( 'anz.cas' )
_ = MessageFactory( 'anz.cas' )

addAnzCentralAuthServiceForm = PageTemplateFile(
    'www/add_anzcentralauthservice_form.pt', globals() )

def manage_addAnzCentralAuthService( self, id, title=None, REQUEST=None ):
    ''' Add an instance of anz cas to PAS. '''
    obj = AnzCentralAuthService( id, title )
    self._setObject( obj.getId(), obj )
    
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '%s/manage_workspace'
            '?manage_tabs_message='
            'AnzCentralAuthService+added.'
            % self.absolute_url()
            )

class AnzCentralAuthService( BasePlugin ):
    ''' Anz Central Authentication Service.
    Implement as a PAS plugin.
    
    '''
    
    implements( IAnzCentralAuthService, IServicesManager )
    
    meta_type = 'Anz Central Auth Service'
    
    # Cookie variable use to save ticket granting ticket
    tgt_cookie_name = '__cas_tgt'
    
    # Boolean variable denoting whether secure connection is required or not.
    requireSecure = True
    
    # Where to send people for logging in, default is Plone's stock
    # 'login_form'.
    loginPagePath = 'login_form'
    
    security = ClassSecurityInfo()
    
    #
    # ZMI
    #
    manage_options = ( 
        ( { 'label': 'Services', 
            'action': 'manage_services', 
            },
          )
        + BasePlugin.manage_options
        )
    
    security.declareProtected( ManagePortal, 'manage_services' )
    manage_services = PageTemplateFile( 'www/manage_services.pt',
                                     globals(),
                                     __name__='manage_services'
                                     )
    
    _properties = (
        {
            'id': 'requireSecure',
            'lable': 'Require Secure',
            'type': 'boolean',
            'mode': 'w'
            },
        {
            'id': 'loginPagePath',
            'lable': 'Login Page Path',
            'type': 'string',
            'mode': 'w'
            },
        )
    
    security.declareProtected( ManagePortal, 'manage_removeServices' )
    def manage_removeServices( self, service_ids=[] ):
        ''' Remove one or more services via the ZMI. '''
        if not service_ids:
            message = 'No+services+selected'
        else:
            for id in service_ids:
                self.deleteService( id )
            
            message = 'Services+removed'
            
        self.REQUEST.RESPONSE.redirect(
            '%s/manage_services?manage_tabs_message=%s'
            % ( self.absolute_url(), message )
            )
    
    security.declareProtected( ManagePortal, 'manage_addService' )
    def manage_addService( self, id, name='', description='',
                           enabled=False, ssoEnabled=False,
                           anonymousAccess=False, allowedToProxy=False ):
        ''' Add a service via the ZMI. '''
        adding = False
        msg = None
        if not id:
            msg = 'ID+is+required.'
            adding = True
        elif id in self._services.keys():
            msg = 'This+ID+has+been+used+already.'
            adding = True
        else:
            msg = 'Service+added'
            self.addService( id, name, description, enabled,
                             ssoEnabled, anonymousAccess,
                             allowedToProxy )
        
        url = '%s/manage_services?manage_tabs_message=%s' % \
            ( self.absolute_url(), msg )
        if adding:
            url += '&adding=1'
        
        self.REQUEST.RESPONSE.redirect( url )
    
    security.declareProtected( ManagePortal, 'manage_editService' )
    def manage_editService( self, id, name='', description='',
                            enabled=False, ssoEnabled=False,
                            anonymousAccess=False, allowedToProxy=False ):
        ''' Edit a service via the ZMI. '''
        assert id in self._services.keys()
        
        self.editService( id, name, description, enabled,
                          ssoEnabled, anonymousAccess,
                          allowedToProxy )
        
        self.REQUEST.RESPONSE.redirect(
            '%s/manage_services?manage_tabs_message=%s'
            % ( self.absolute_url(), 'Service+edited' )
            )
    
    def __init__( self, id, title ):
        self._id = self.id = id
        self.title = title
        
        # registered service manager
        self._services = OOBTree()
        
        # ticket granting ticket registry
        # tgt validate in 2 hours
        self._ticketRegistry = OOBForest( timedelta(hours=1), count=3 )
        
        # service ticket registry
        # st validate in 5 minutes
        self._serviceTicketRegistry = OOBForest( timedelta(minutes=1),
                                                 count=6 )
    
    #
    # Registered Service Manager
    #
    security.declareProtected( ManagePortal, 'addService' )
    def addService( self, id, name='', description='',
                    enabled=True, ssoEnabled=True,
                    anonymousAccess=False, allowedToProxy=True ):
        ''' See interfaces.IServicesManager. '''
        registeredService = RegisteredService( 
            id, name, description, enabled,
            ssoEnabled, anonymousAccess, allowedToProxy )
        
        self._services[id] = registeredService
    
    security.declareProtected( ManagePortal, 'editService' )
    def editService( self, id, name, description,
                     enabled, ssoEnabled,
                     anonymousAccess, allowedToProxy ):
        ''' See interfaces.IServicesManager. '''
        assert id in self._services.keys()
        
        self._services[id] = RegisteredService( 
            id, name, description, enabled,
            ssoEnabled, anonymousAccess, allowedToProxy )
    
    security.declareProtected( ManagePortal, 'deleteService' )
    def deleteService( self, id ):
        ''' See interfaces.IServicesManager. '''
        assert id in self._services.keys()
        del self._services[id]
    
    security.declareProtected( ManagePortal, 'findServiceBy' )
    def findServiceBy( self, service ):
        ''' See interfaces.IServicesManager. '''
        ret = None
        for key in self._services.keys():
            s = self._services[key]
            if s.matches(service):
                ret = s
                break
        
        return ret
    
    security.declareProtected( ManagePortal, 'findServiceById' )
    def findServiceById( self, id ):
        ''' See interfaces.IServicesManager. '''
        ret = None
        for key in self._services.keys():
            if key == id:
                ret = self._services[key]
                break
        
        return ret
    
    security.declareProtected( ManagePortal, 'getAllServices' )
    def getAllServices( self ):
        ''' See interfaces.IServicesManager. '''
        return [ self._services[k] for k in self._services.keys() ]
    
    #
    # Central Auth Service Core
    #
    security.declarePublic( 'login' )
    def login( self, service=None, renew=None, gateway=None ):
        ''' See interfaces.IAnzCentralAuthService. '''
        request = self.REQUEST
        response = request.RESPONSE
        
        try:
            try:
                credentials = None
                tgtId = self._getTGTFromCookie()
                if tgtId:
                    # force the user to re-authenticate
                    if renew == 'true':
                        return response._unauthorized()
                else:
                    # redirect to service when 'gateway' is set. if both 'renew'
                    # and 'gateway' are set, it act as if 'gateway' is not set.
                    if (gateway=='true') and (renew!='true') and service:
                        return response.redirect( unquote(service) )
                    
                    # challenge anonymous user
                    user = getSecurityManager().getUser()
                    if user.getUserName() == 'Anonymous User' and \
                       'Authenticated' not in user.getRoles():
                        return response._unauthorized()
                    
                    # generate tgt and tgc
                    credentials = self._createCredentials()
                    tgtId = self._createTicketGrantingTicket( credentials )
                    self._addTicketGrantingCookie( tgtId )
            except BaseException, e:
                LOG.warning( e )
                return self._redirectErrorPage( e )
            else:
                if service:
                    try:
                        # get credentials for authenticated user
                        user = getSecurityManager().getUser()
                        if user.getUserName() == 'Anonymous User' and \
                           'Authenticated' not in user.getRoles():
                            credentials = None
                        else:
                            credentials = self._createCredentials()
                        
                        serviceObj = Service( unquote(service) )
                        stId = self._grantServiceTicket( tgtId,
                                                         serviceObj,
                                                         credentials )
                        
                        return response.redirect( '%s?ticket=%s' % \
                                                  (service,stId) )
                    except UnauthorizedSsoServiceException, e:
                        LOG.warning( e )
                        
                        casError = _( unicode(e.ERROR_DESC) )
                        casErrorMsg = str( e )
                        reAuthUrl = '%s/login?service=%s&renew=true' % \
                                  (self.absolute_url(),service)
                        return response.redirect(
                            '%s/cas_error?casError=%s&casErrorMsg=%s&reAuthUrl=%s' \
                            % (self.absolute_url(), casError,
                               casErrorMsg,quote(reAuthUrl)) )
                    except BaseException, e:
                        LOG.warning( e )
                        return self._redirectErrorPage( e )
                else:
                    # show cas_login_success page if no service provide
                    return response.redirect( '%s/cas_login_success' % \
                                              self.absolute_url() )
        finally:
            # remove authentication credentials from CAS after login
            acl = self._getUserFolder()
            acl.resetCredentials( request, response )
    
    security.declarePublic( 'logout' )
    def logout( self, url=None ):
        ''' See interfaces.IAnzCentralAuthService. '''
        tgtId = self._getTGTFromCookie()
        
        # if we get a tgc from cookie, send logout request to all related
        # service, or maybe this is came from an anoymouse user, redirect
        # to logout page directly
        if tgtId:
            acl = self._getUserFolder()
            acl.resetCredentials( self.REQUEST, self.REQUEST.RESPONSE )
            
            self._destroyTicketGrantingTicket( tgtId )
            self._removeTicketGrantingCookie()
        
        redirectUrl = '%s/cas_logout' % self.absolute_url()
        if url:
            redirectUrl += '?url=%s' % quote(url)
        
        return self.REQUEST.RESPONSE.redirect( redirectUrl )
    
    security.declarePublic( 'validate' )
    def validate( self, service, ticket, renew=None ):
        ''' See interfaces.IAnzCentralAuthService. '''
        try:
            if not service or not ticket:
                raise InvalidRequestException
            
            service = unquote( service )
            serviceObj = Service( service )
            assertion = self._validateServiceTicket( serviceObj, ticket )
            
            # satisfy validation specification
            vs = CAS10ValidationSpecification( renew )
            if not vs.isSatisfiedBy( assertion ):
                raise InvalidTicketException(
                    'St %s does not satisfy validation specification.' % \
                    ticket )
        except BaseException, e:
            LOG.warning( e )
            return 'no\n\n'
        else:
            userId = assertion.getChainedAuthentications()[-1].\
                   getPrincipal().getId()
            return 'yes\n%s\n' % userId
    
    security.declarePublic( 'serviceValidate' )
    def serviceValidate( self, service, ticket, pgtUrl=None, renew=None ):
        ''' See interfaces.IAnzCentralAuthService. '''
        try:
            if not service or not ticket:
                raise InvalidRequestException
            
            service = unquote( service )
            serviceObj = Service( service )
            
            pgtId = None
            if pgtUrl:
                try:
                    pgtUrl = unquote( pgtUrl )
                    credentials = self._createCredentials( pgtUrl )
                    pgtId = self._delegateTicketGrantingTicket( ticket,
                                                                credentials )
                except BaseException, e:
                    LOG.warning( e )
                except Exception, e:
                    LOG.warning( e )
            
            assertion = self._validateServiceTicket( serviceObj, ticket )
            
            # satisfy validation specification
            vs = CAS20WithoutProxyingValidationSpecification( renew )
            if not vs.isSatisfiedBy( assertion ):
                raise InvalidTicketException(
                    'St %s does not satisfy validation specification.' % \
                    ticket )
        except BaseException, e:
            LOG.warning( e )
            return self._failureResponse( 'authenticationFailure', e )
        else:
            userId = assertion.getChainedAuthentications()[-1].\
                   getPrincipal().getId()
            
            if pgtUrl and pgtId:
                try:
                    proxyHandler = ProxyHandler()
                    proxyIou = proxyHandler.handle( credentials, pgtId )
                except BaseException, e:
                    LOG.warning( e )
                except Exception, e:
                    LOG.warning( e )
                else:
                    if proxyIou:
                        response = []
                        response.append(
                            '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">'
                            )
                        response.append( '<cas:authenticationSuccess>' )
                        response.append(
                            '<cas:user>%s</cas:user>' % userId )
                        response.append(
                            '<cas:proxyGrantingTicket>%s</cas:proxyGrantingTicket>' % \
                            proxyIou
                            )
                        response.append( '</cas:authenticationSuccess>' )
                        response.append( '</cas:serviceResponse>' )
                        return self._successResponse( ''.join(response) )
            
            # return user info only
            response = []
            response.append(
                '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">'
                )
            response.append( '<cas:authenticationSuccess>' )
            response.append(
                '<cas:user>%s</cas:user>' % userId )
            response.append( '</cas:authenticationSuccess>' )
            response.append( '</cas:serviceResponse>' )
            
            return self._successResponse( ''.join(response) )
    
    security.declarePublic( 'proxyValidate' )
    def proxyValidate( self, service, ticket, pgtUrl=None, renew=None ):
        ''' See interfaces.IAnzCentralAuthService. '''
        try:
            if not service or not ticket:
                raise InvalidRequestException
            
            service = unquote( service )
            serviceObj = Service( service )
            
            pgtId = None
            if pgtUrl:
                try:
                    pgtUrl = unquote( pgtUrl )
                    credentials = self._createCredentials( pgtUrl )
                    pgtId = self._delegateTicketGrantingTicket( ticket,
                                                                credentials )
                except BaseException, e:
                    LOG.warning( e )
                except Exception, e:
                    LOG.warning( e )
            
            assertion = self._validateServiceTicket( serviceObj, ticket )
            
            # satisfy validation specification
            vs = CAS20ValidationSpecification( renew )
            if not vs.isSatisfiedBy( assertion ):
                raise InvalidTicketException(
                    'St %s does not satisfy validation specification.' % \
                    ticket )
        except BaseException, e:
            LOG.warning( e )
            return self._failureResponse( 'authenticationFailure', e )
        except Exception, e:
            LOG.warning( e )
            return self._failureResponse( 'authenticationFailure', e )
        else:
            authentications = assertion.getChainedAuthentications()
            userId = authentications[-1].getPrincipal().getId()
            if pgtUrl and pgtId:
                try:
                    proxyHandler = ProxyHandler()
                    proxyIou = proxyHandler.handle( credentials, pgtId )
                except BaseException, e:
                    LOG.warning( e )
                except Exception, e:
                    LOG.warning( e )
                else:
                    if proxyIou:
                        response = []
                        response.append(
                            '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">'
                            )
                        response.append( '<cas:authenticationSuccess>' )
                        response.append(
                            '<cas:user>%s</cas:user>' % userId )
                        response.append(
                            '<cas:proxyGrantingTicket>%s</cas:proxyGrantingTicket>' \
                            % proxyIou
                            )
                        
                        # proxies
                        if len(authentications) > 1:
                            response.append( '<cas:proxies>' )
                            for a in authentications[:-1]:
                                response.append( '<cas:proxy>%s</cas:proxy>' \
                                                 % a.getPrincipal().getId() )
                            response.append( '</cas:proxies>' )
                        
                        response.append( '</cas:authenticationSuccess>' )
                        response.append( '</cas:serviceResponse>' )
                        
                        return self._successResponse( ''.join(response) )
            
            # return user info only
            response = []
            response.append(
                '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">'
                )
            response.append( '<cas:authenticationSuccess>' )
            response.append(
                '<cas:user>%s</cas:user>' % userId )
            
            # proxies
            if len(authentications) > 1:
                response.append( '<cas:proxies>' )
                for a in authentications[:-1]:
                    response.append( '<cas:proxy>%s</cas:proxy>' % \
                                     a.getPrincipal().getId() )
                response.append( '</cas:proxies>' )
            
            response.append( '</cas:authenticationSuccess>' )
            response.append( '</cas:serviceResponse>' )
            return self._successResponse( ''.join(response) )
    
    security.declarePublic( 'proxy' )
    def proxy( self, pgt, targetService ):
        ''' See interfaces.IAnzCentralAuthService. '''
        try:
            if not pgt or not targetService:
                raise InvalidRequestException
            
            serviceObj = Service( unquote(targetService) )
            
            ptId = self._grantServiceTicket( pgt, serviceObj )
        except BaseException, e:
            LOG.warning( e )
            return self._failureResponse( 'proxyFailure', e )
        else:
            response = []
            response.append(
                '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">'
                )
            response.append( '<cas:proxySuccess>' )
            response.append(
                '<cas:proxyTicket>%s</cas:proxyTicket>' % ptId )
            response.append( '</cas:proxySuccess>' )
            response.append( '</cas:serviceResponse>' )
            return self._successResponse( ''.join(response) )
    
    #
    # Challenge Plugin
    #
    security.declarePrivate( 'challenge' )
    def challenge( self, request, response, **kw ):
        ''' Challenge the user for credentials when 'renew' parameter found.
        '''
        # short-circuit when no 'loginPagePath' setting
        url = self._getLoginPageUrl()
        if not url:
            return 0
        
        # short-circuit when no 'renew=true' found in query string
        query_string = request['QUERY_STRING']
        query = [ s for s in query_string.split('&') \
                  if s.find('renew=')==0 ]
        if (not query) or (query[0]!='renew=true'):
            return 0
        
        # The following codes are copied from CookieAuthHelper.py
        came_from = request.get( 'came_from', None )
        if came_from is None:
            came_from = request.get( 'ACTUAL_URL', '' )
            
            # Trip 'renew' parameter to avoid infinite cycle.
            # Because when both 'renew' and 'gateway' are set, it act as
            # only 'renew' is set, so trip 'gateway' parameter too.
            query = [ s for s in query_string.split('&') \
                      if (s.find('renew=')!=0 and s.find('gateway=')!=0) ]
            query = '&'.join( query )
            if query:
                if not query.startswith('?'):
                    query = '?' + query
                came_from += query
        else:
            # If came_from contains a value it means the user
            # must be coming through here a second time
            # Reasons could be typos when providing credentials
            # or a redirect loop (see below)
            req_url = request.get( 'ACTUAL_URL', '' )
            
            if req_url and req_url == url:
                # Oops... The login_form cannot be reached by the user -
                # it might be protected itself due to misconfiguration -
                # the only sane thing to do is to give up because we are
                # in an endless redirect loop.
                return 0
        
        url += '?came_from=%s' % quote( came_from )
        response.redirect( url, lock=1 )
        return 1
    
    #
    # private help func
    #
    security.declarePrivate( '_getLoginPageUrl' )
    def _getLoginPageUrl( self ):
        ''' Return where to send people for logging in. '''
        path = None
        if self.loginPagePath:
            path = '%s/%s' % ( self.absolute_url(), self.loginPagePath )
        
        return path
    
    security.declarePrivate( '_getUserFolder' )
    def _getUserFolder( self ):
        ''' Safely retrieve a User Folder to work with. '''
        return getattr( self, 'acl_users', None )
    
    security.declarePrivate( '_createCredentials' )
    def _createCredentials( self, pgtUrl=None ):
        ''' Create credentials object. '''
        credentials = None
        if pgtUrl:
            credentials = HttpBasedServiceCredentials( pgtUrl )
        else:
            userId = getSecurityManager().getUser().getUserName()
            credentials = UsernameCredentials( userId )
        
        return credentials
    
    security.declarePrivate( '_redirectErrorPage' )
    def _redirectErrorPage( self, exception ):
        ''' Redirect to error page.
        
        @param exception
        exception object
        
        '''
        casError = _( unicode(exception.ERROR_DESC or exception.ERROR_CODE) )
        casErrorMsg = str( exception )
        return self.REQUEST.RESPONSE.redirect(
            '%s/cas_error?casError=%s&casErrorMsg=%s' % \
            ( self.absolute_url(), casError, casErrorMsg ) )
    
    security.declarePrivate( '_failureResponse' )
    def _failureResponse( self, failureType, exception ):
        ''' Compose a failure response.
        
        @param failureType
        failure type, act as the element name of core node.
        one of ('authenticationFailure', 'proxyFailure')
        
        @param exception
        exception object
        
        @return string
        a xml response contains failure contents
        
        '''
        response = self.REQUEST.RESPONSE
        response.setHeader( 'Content-Type', 'text/xml;charset=utf-8' )
        
        body = []
        body.append(
            '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">'
            )
        body.append( '<cas:%s code="%s">' % \
                     (failureType,exception.ERROR_CODE) )
        body.append( escape(str(exception)) )
        body.append( '</cas:%s>' % failureType )
        body.append( '</cas:serviceResponse>' )
        
        return ''.join( body )
    
    security.declarePrivate( '_successResponse' )
    def _successResponse( self, body ):
        ''' Compose a success response.
        
        @param body
        full contents of the response
        
        @return string
        a xml response contains success contents
        
        '''
        response = self.REQUEST.RESPONSE
        response.setHeader( 'Content-Type', 'text/xml;charset=utf-8' )
        return body
    
    security.declarePrivate( '_grantServiceTicket' )
    def _grantServiceTicket( self, tgtId, service, credentials=None ):
        ''' Grant a ServiceTicket for a Service *if* the principal resolved
        from the credentials matches the principal associated with the
        TicketGrantingTicket.
        
        @param tgtId
        Proof of prior authentication
        
        @param service
        The target service of the ServiceTicket
        
        @param credentials
        The Credentials to present to receive the ServiceTicket
     
        @return
        The ServiceTicket for target Service.
        
        '''
        if not tgtId or not service:
            raise InvalidRequestException
        
        if not tgtId in self._ticketRegistry.keys():
            raise InvalidTicketException( 'No tgt found by id %s' % tgtId )
        
        tgt = self._ticketRegistry[tgtId]
        if tgt.isExpired():
            del self._ticketRegistry[tgtId]
            raise InvalidTicketException( 'Tgt %s has been expired.' % tgtId )
        
        # validate when registered services is not empty
        if self.getAllServices():
            registeredService = self.findServiceBy( service )
            if not registeredService or not registeredService.isEnabled():
                raise UnauthorizedServiceException( 'Service %s not registered.' % \
                                                    registeredService.getId() )
            
            if not registeredService.isSsoEnabled() and \
               not credentials and \
               tgt.getCountOfUses()>0:
                raise UnauthorizedSsoServiceException(
                    'Service %s not allowed to use SSO' % registeredService.getId() )
        
        # check credentials
        if credentials:
            # construct authentication manager
            authenticationManager = AuthenticationManager( [
                UsernameCredentialAuthenticationHandler(),
                HttpBasedServiceCredentialsAuthenticationHandler(
                    self.requireSecure)
                ] )
            
            authentication = authenticationManager.authenticate( 
                credentials )
            originalAuthentication = tgt.getAuthentication()
            if authentication.getPrincipal().getId() != \
               originalAuthentication.getPrincipal().getId():
                raise AuthenticationException(
                    'Tgt %s has different authentication.' % tgtId )
        
        stId = genUniqueId( ServiceTicket.PREFIX )
        st = tgt.grantServiceTicket( stId, service, not not credentials )
        self._serviceTicketRegistry[stId] = st
        
        return stId
    
    security.declarePrivate( '_delegateTicketGrantingTicket' )
    def _delegateTicketGrantingTicket( self, stId, credentials ):
        ''' Delegate a TicketGrantingTicket to a Service for proxying
        authentication to other Services.
        
        @param stId
        The service ticket that will delegate to a TicketGrantingTicket
        
        @param credentials
        The credentials of the service that wishes to have a
        TicketGrantingTicket delegated to it.
        
        @return
        TicketGrantingTicket that can grant ServiceTickets that proxy
        authentication.
        
        '''
        if not stId in self._serviceTicketRegistry.keys():
            raise InvalidTicketException( 'No st found by id %s.' % stId )
        
        st = self._serviceTicketRegistry[stId]
        if st.isExpired():
            raise InvalidTicketException( 'St %s has been expired.' % stId )
        
        # validate when registered services is not empty
        if self.getAllServices():
            registeredService = self.findServiceBy( st.getService() )
            if not registeredService or not registeredService.isEnabled() or \
               not registeredService.isAllowedToProxy():
                raise UnauthorizedProxyingException(
                    'Service %s attempted to proxy, but is not allowed.' % \
                    registeredService.getId() )
        
        # construct authentication manager
        authenticationManager = AuthenticationManager( [
            UsernameCredentialAuthenticationHandler(),
            HttpBasedServiceCredentialsAuthenticationHandler(
                self.requireSecure)
            ] )
        
        authentication = authenticationManager.authenticate( credentials )
        id = genUniqueId( TicketGrantingTicket.PREFIX )
        tgt = st.grantTicketGrantingTicket( id, authentication )
        
        self._ticketRegistry[id] = tgt
        
        return id
    
    security.declarePrivate( '_validateServiceTicket' )
    def _validateServiceTicket( self, service, stId ):
        ''' Validate a ServiceTicket for a particular Service.
        
        @param service
        Service wishing to validate a prior authentication.
        
        @param stId
        roof of prior authentication.
        
        @return
        an assertion object contains validation information
        
        '''
        if not stId in self._serviceTicketRegistry.keys():
            raise InvalidTicketException( 'No st found by id %s.' % stId )
        
        st = self._serviceTicketRegistry[stId]
        
        # validate when registered services is not empty
        if self.getAllServices():
            registeredService = self.findServiceBy( service )
            if not registeredService or not registeredService.isEnabled():
                raise UnauthorizedServiceException(
                    'Service %s not registered.' % registeredService.getId() )
        
        try:
            try:
                if st.isExpired():
                    raise InvalidTicketException( 'St %s has been expired.' % stId )
                
                if not st.isValidFor( service ):
                    raise ServiceValidationException(
                        'St %s with service %s does not match supplied service %s' \
                        % ( stId, st.getService().getId(), service.getId() ) )
            except BaseException, e:
                LOG.warning( e )
                raise
            else:
                authentications = st.getGrantingTicket().getChainedAuthentications()
                
                # Use random string as user id when 'anonymousAccess'
                newAuthentications = deepcopy( authentications )
                registeredService = self.findServiceBy( service )
                if registeredService and registeredService.isAnonymousAccess():
                    newAuthentications[-1].getPrincipal().id = \
                                      genUniqueId( 'anonymous' )
                
                return Assertion( service,
                                  newAuthentications, st.isFromNewLogin() )
        finally:
            del self._serviceTicketRegistry[stId]
    
    security.declarePrivate( '_createTicketGrantingTicket' )
    def _createTicketGrantingTicket( self, credentials ):
        ''' Create a TicketGrantingTicket based on opaque credentials supplied
        by the caller.
        
        @credentials
        The credentials to create the ticket for
        
        @return
        The String identifier of the ticket (may not be null).
        
        '''
        id = genUniqueId( TicketGrantingTicket.PREFIX )
        
        # construct authentication manager
        authenticationManager = AuthenticationManager( [
            UsernameCredentialAuthenticationHandler(),
            HttpBasedServiceCredentialsAuthenticationHandler(
                self.requireSecure)
            ] )
        
        authentication = authenticationManager.authenticate( credentials )
        tgt = TicketGrantingTicket( id, None, authentication )
        self._ticketRegistry[id] = tgt
        
        return id
    
    security.declarePrivate( '_addTicketGrantingCookie' )
    def _addTicketGrantingCookie( self, tgt ):
        ''' Handles the TicketGrantingTicket creation and destruction.
        If there is an old one exists, the old one is destroyed and replaced
        with the new one.
        
        @param tgt
        new ticket granting ticket will be added to cookie
        
        '''
        cookieTgt = self._getTGTFromCookie()
        kw = {
            'domain': self._getDomainName(),
            'path': '/'.join(self.getPhysicalPath()),
            }
        
        if self.requireSecure:
            kw['secure'] = 1
        
        response = self.REQUEST.RESPONSE
        response.setCookie( self.tgt_cookie_name, quote(tgt), **kw )
        
        # destroy old tgt cookie if a new one generated
        if cookieTgt and cookieTgt!=tgt:
            self._destroyTicketGrantingTicket( cookieTgt )
    
    def _removeTicketGrantingCookie( self ):
        ''' Expire TicketGrantingTicket cookie from browser. '''
        response = self.REQUEST.RESPONSE
        response.expireCookie( self.tgt_cookie_name,
                               #domain=self._getDomainName(),
                               path='/'.join(self.getPhysicalPath()),
                               )
    
    security.declarePrivate( '_destroyTicketGrantingTicket' )
    def _destroyTicketGrantingTicket( self, tgtId ):
        ''' Destroy a TicketGrantingTicket. This has the effect of invalidating
        any Ticket that was derived from the TicketGrantingTicket being
        destroyed.
        
        @param tgtId
        the id of the ticket we want to destroy
        
        '''
        assert tgtId in self._ticketRegistry.keys(), ''
        
        tgt = self._ticketRegistry[tgtId]
        tgt.expire()
        del self._ticketRegistry[tgtId]
    
    security.declarePrivate( '_getTGTFromCookie' )
    def _getTGTFromCookie( self ):
        ''' Get ticket granting ticket from request cookie. '''
        ret = None
        cookies = self.REQUEST.cookies
        if cookies.has_key( self.tgt_cookie_name ):
            ret = cookies[self.tgt_cookie_name]
        
        return ret
    
    def _getDomainName( self ):
        ''' Extract domain name in virtual host safe manner from request.
        
        @return
        Host DNS name of CAS located in. Lowercased, no port part.
        Return None if host name is not present in HTTP request headers
        (e.g. unit testing).
        
        '''
        request = self.REQUEST
        
        if 'HTTP_X_FORWARDED_HOST' in request.environ:
            # Virtual host
            host = request.environ['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in request.environ:
            # Direct client request
            host = request.environ['HTTP_HOST']
        else:
            return None
        
        # separate to domain name and port sections
        return host.split(':')[0].lower()
        #return host

classImplements( AnzCentralAuthService, 
                 IChallengePlugin
                 )

InitializeClass( AnzCentralAuthService )
