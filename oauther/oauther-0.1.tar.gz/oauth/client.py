##################################################################################
##
## The MIT License
## 
## Copyright (c) 2007 Leah Culver
## Copyright (c) 2009 Luis C. Cruz
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.
##
##################################################################################

from token import OAuthToken
from exceptions import OAuthError
from data import OAuthDataStoreMixin

class OAuthClient(object):
    """OAuthClient is a worker to attempt to execute a request."""
 
    def __init__(self, oauth_consumer, opener):
        """ Parameters:
            oauth_consumer - an OAuthConsumer object
            opener - an urllib2's OpenerDirector object
        """
        self._consumer = oauth_consumer
        self._token = None
        self._oauth_datastore = None
        self._callback_url = None
        self.opener = opener
    
    def get_token(self):
        if self._token is None:
            self._token = self.oauth_datastore.lookup_token()
        return self._token
    
    token = property(get_token)

    def get_consumer(self):
        return self._consumer

    consumer = property(get_consumer)
    
    def set_callback_url(self, callback_url):
        self._callback_url = callback_url
    
    def get_callback_url(self):
        return self._callback_url
    
    def _get_oauth_datastore(self):
        """If oauth_datastore is None raise an OAuthError, is necesary
        to set this field before.
        """
        if self._oauth_datastore is None:
            raise OAuthError('OAuthDatastore is None.')
        return self._oauth_datastore
    
    def _set_oauth_datastore(self, oauth_datastore):
        """If oauth_datastore is not an OAuthDataStoreMixin instance
        raise an OAuthError. To ensure providing the necesary methods.
        """
        if isinstance(oauth_datastore, OAuthDataStoreMixin):
            self._token = None # this clear cache and next call get data from oauth_datastore
            self._oauth_datastore = oauth_datastore
        else:
            raise OAuthError('%s is not a valid OAuthDataStoreMixin instance.'%(oauth_datastore))
    
    oauth_datastore = property(_get_oauth_datastore,
                               _set_oauth_datastore,
                               doc='Used to save the token')
 
    def _get_request_request(self, *arg, **karg):
        """-> OAuthRequest."""
        raise NotImplementedError
    
    def _get_access_request(self, *arg, **karg):
        """-> OAuthRequest."""
        raise NotImplementedError
    
    def _get_resource_request(self, *arg, **karg):
        """-> OAuthRequest."""
        raise NotImplementedError
    
    def _get_authorize_request(self, *arg, **karg):
        """-> OAuthRequest."""
        raise NotImplementedError
    
    def _get_signature_method(self):
        """-> OAuthSignatureMethod."""
        raise NotImplementedError
    
    def _fetch_request_token(self):
        """Fetch for the request token.
        
        @return OAuthToken
        @raises OAuthError if is unable to retrieve the token.
        @raises urllib2.HTTPError if is unable to retrieve the token.
        """        
        # generate the request
        oauth_request = self._get_request_request()
        oauth_request.sign_request(self._get_signature_method(), self.consumer, None)
        # fecthing tokens
        response = self.opener.open(oauth_request.to_url())
        try:            
            result = response.read()
        except IOError, error:
            error_str = "Error retrieving request token.\n Cause: '%s'"%str(error)
            raise OAuthError(error_str)
        finally:
            response.close()
        return OAuthToken.from_string(result)
    
    def is_authorized(self):
        """Verify if the client is authorized to access resources."""
        return self.token is not None
    
    def deauthorize(self):
        """Remove the access token from the oauth_datastore object"""
        self.oauth_datastore.delete_token()
        self._token = None
    
    def fetch_for_authorize(self):
        """Fetch for the authorize and the url where to redirect.
        
        @return url, token
        url is the authorize request url if is a request token, 
        and return the token.
        """
        self._token = self._fetch_request_token()
        self._token.set_callback(self.get_callback_url())
        oauth_request = self._get_authorize_request()
        oauth_request.sign_request(self._get_signature_method(), self.consumer, self.token)
        token, self._token = self._token, None
        return (oauth_request.to_url(), token)
    
    def fetch_access_token(self, token):
        """Fetch for the access token.
        
        @param token is request token returned by fetch_for_authorize method.
        @raise OAuthError if is unable to retrieve the token.
        @raise urllib2.HTTPError
        
        The param token is necesary for web applications. Which creates
        new objects in each request.
        """
        if isinstance(token, OAuthToken):
            # generate the request
            self._token = token
            oauth_request = self._get_access_request()
            oauth_request.sign_request(self._get_signature_method(), self.consumer, self.token)
            # fecthing tokens
            response = self.opener.open(oauth_request.to_url())
            try:
                result = response.read()
            except IOError, error:
                error_str = "Error retrieving access token.\n Cause: '%s'"%str(error)
                self._token = None
                raise OAuthError(error_str)
            finally:
                response.close()                
            # creating and saving access token
            self._token = OAuthToken.from_string(result)
            self.oauth_datastore.save_token(self._token)
        else:
            raise ValueError('The token "%s" is not valid for this session.'%token)
    
    def fetch_resource(self, url, parameters=None, http_method='GET'):
        """ Return a file object to read data.
        
        raise urllib2.HTTPError
        """
        oauth_request = self._get_resource_request(url, parameters, http_method)
        oauth_request.sign_request(self._get_signature_method(), self.consumer, self.token)
        if http_method == 'GET':
            response = self.opener.open(oauth_request.to_url())
        elif http_method == 'POST':
            response = self.opener.open(oauth_request.http_url, oauth_request.to_postdata())
        return response