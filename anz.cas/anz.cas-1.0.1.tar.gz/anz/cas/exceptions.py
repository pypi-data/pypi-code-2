
class BaseException( Exception ):
    ''' Base class for exceptions in this module. '''
    pass

class InvalidTicketException( BaseException ):
    ''' '''
    ERROR_CODE = 'INVALID_TICKET'
    ERROR_DESC = ''

class ServiceValidationException( BaseException ):
    ''' '''
    ERROR_CODE = 'INVALID_SERVICE'
    ERROR_DESC = ''

class InvalidRequestException( BaseException ):
    ''' '''
    ERROR_CODE = 'INVALID_REQUEST'
    ERROR_DESC = ''
    
    def __str__( self ):
        return 'Not all of the required request parameters were present.'

class InternalException( BaseException ):
    ''' '''
    ERROR_CODE = 'INTERNAL_ERROR'
    ERROR_DESC = ''

class AuthenticationException( BaseException ):
    ''' '''
    ERROR_CODE = 'INVALID_AUTHENTICATION'
    ERROR_DESC = ''

class UnauthorizedServiceException( BaseException ):
    ''' Exception that is thrown when an Unauthorized Service attempts
    to use CAS.
    
    '''
    ERROR_CODE = 'UNAUTHORIZED_SERVICE'
    ERROR_DESC = 'Application Not Authorized to Use CAS.'

class UnauthorizedSsoServiceException( BaseException ):
    ''' Exception thrown when a service attempts to use SSO when it should
    not be allowed to.
    
    '''
    ERROR_CODE = 'UNAUTHORIZED_SSO_SERVICE'
    ERROR_DESC = 'Re-Authentication Required to Access this Service.'

class UnauthorizedProxyingException( BaseException ):
    ''' Exception thrown when a service attempts to proxy when it is not
    allowed to.
    
    '''
    ERROR_CODE = 'UNAUTHORIZED_PROXY_SERVICE'
    ERROR_DESC = ''
