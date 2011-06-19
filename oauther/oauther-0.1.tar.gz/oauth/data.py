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


class OAuthDataStoreMixin(object):
    """Abstract model
    
    The oauth_datastore field in OAuthClient should implement this
    class, if another instance object is trying to set this raise 
    an exception.
    """
 
    def save_token(self, oauth_token):
        """-> OAuthToken."""
        raise NotImplementedError
    
    def delete_token(self):
        """-> OAuthToken."""
        raise NotImplementedError
    
    def lookup_token(self):
        """Should ensure to return a valid token or None. -> OAuthToken."""
        raise NotImplementedError