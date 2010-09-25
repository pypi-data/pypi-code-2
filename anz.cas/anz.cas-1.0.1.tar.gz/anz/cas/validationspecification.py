
# zope
from zope.interface import implements

from anz.cas.interfaces import IValidationSpecification

class BaseValidationSpecification( object ):
    ''' Base validation specification for the CAS protocol.
    This specification checks for the presence of renew=true and if requested,
    succeeds only if ticket validation is occurring from a new login.
    
    '''
    
    implements( IValidationSpecification )
    
    def __init__( self, renew=False ):
        ''' Construct a validation specification object. '''
        self.renew = renew
    
    def isSatisfiedBy( self, assertion ):
        ''' See interfaces.IValidationSpecification. '''
        return self._isSatisfiedByInternal(assertion) and \
               ((not self.renew) or (assertion.isFromNewLogin() and self.renew))
    
    def _isSatisfiedByInternal( self, assertion ):
        # Template method to allow for additional checks by subclassed methods
        # without needing to call super.isSatisfiedBy(...).
        raise NotImplementedError

class CAS10ValidationSpecification( BaseValidationSpecification ):
    ''' Validation specification for the CAS 1.0 protocol.
    This specification checks for the presence of renew=true and if requested,
    succeeds only if ticket validation is occurring from a new login.
    Additionally, validation will fail if passed a proxy ticket.
    
    '''
    def _isSatisfiedByInternal( self, assertion ):
        return len(assertion.getChainedAuthentications()) == 1

class CAS20ValidationSpecification( BaseValidationSpecification ):
    ''' Validation specification for the CAS 2.0 protocol.
    This specification extends the CAS10ValidationSpecification,
    checking for the presence of renew=true and if requested, succeeding only
    if ticket validation is occurring from a new login.
    
    '''
    def _isSatisfiedByInternal( self, assertion ):
        return True

class CAS20WithoutProxyingValidationSpecification( BaseValidationSpecification ):
    ''' Validation specification for the CAS 2.0 protocol.
    This specification extends the CAS20ValidationSpecification, checking for
    the presence of renew=true and if requested, succeeding only if ticket
    validation is occurring from a new login. Additionally, this specification
    will not accept proxied authentications.
    
    '''
    def _isSatisfiedByInternal( self, assertion ):
        return len(assertion.getChainedAuthentications()) == 1
