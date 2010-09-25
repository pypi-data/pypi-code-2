
# zope
from zope.interface import implements

from anz.cas.interfaces import IProxyHandler
from anz.cas.utils import genUniqueId, isValidEndPoint

class ProxyHandler( object ):
    ''' See interfaces.IProxyHandler. '''
    
    implements( IProxyHandler )
    
    PGTIOU_PREFIX = 'PGTIOU'
    
    def handle( self, credentials, pgtId ):
        ''' See interfaces.IProxyHandler. '''
        pgtUrl = credentials.getCallbackUrl()
        proxyIou = genUniqueId( self.PGTIOU_PREFIX )
        
        if pgtUrl.find('?') == -1:
            pgtUrl += '?'
        else:
            pgtUrl += '&'
        
        pgtUrl += 'pgtIou='
        pgtUrl += proxyIou
        pgtUrl += '&pgtId='
        pgtUrl += pgtId
        
        # validate pgtUrl
        if isValidEndPoint( pgtUrl ):
            return proxyIou
