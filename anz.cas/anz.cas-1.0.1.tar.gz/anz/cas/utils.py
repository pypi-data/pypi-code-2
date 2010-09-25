
# python
import socket
from urllib import urlencode
from urllib2 import urlopen, Request, URLError, HTTPError
from logging import getLogger

from uuid import uuid1

LOG = getLogger( 'anz.cas' )

def genUniqueId( prefix='' ):
    ''' Return a unique id.
    
    @param prefix
    prefix of the unique id
    
    @return string
    An unique id with specified prefix.
    
    '''
    return prefix + '-' + str(uuid1())

def isValidEndPoint( url ):
    ''' Check if the specific url can be connected successfully or not.
    
    @param url
    url to be connected
    
    @return boolean
    True means connection success, False means failure.
    
    '''
    ret = False
    socket.setdefaulttimeout( 5 )
    try:
        response = urlopen( url )
    except HTTPError, e:
        LOG.warning( 'The server couldn\'t fulfill the request.' )
        LOG.warning( 'Error code: %s'% e.code )
    except URLError, e:
        LOG.warning( 'We failed to reach a server.' )
        LOG.warning( 'Reason: %s'% e.reason )
    else:
        ret = True
    
    return ret

def sendMessageToEndPoint( url, msg, async=False ):
    ''' Sends a message to a particular endpoint.
    Option of sending it without waiting to ensure a response was returned.
    
    @param url
    the url to send the message to
    
    @param msg
    the message itself
    
    @param async
    true if you don't want to wait for the response, false otherwise.
    
    @return boolean
    if the message was sent, or async was used.  false if the message failed.
    
    '''
    ret = False
    
    socket.setdefaulttimeout( 5 )
    try:
        values = { 'logoutRequest': msg }
        data = urlencode( values )
        req = Request( url, data )
        response = urlopen( req )
    except HTTPError, e:
        LOG.warning( 'The server couldn\'t fulfill the request.' )
        LOG.warning( 'Error code: %s' % e.code )
    except URLError, e:
        LOG.warning( 'We failed to reach a server.' )
        LOG.warning( 'Reason: %s' % e.reason )
    else:
        ret = True
    
    return ret
