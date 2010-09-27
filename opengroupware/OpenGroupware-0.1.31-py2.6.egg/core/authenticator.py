# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import logging
from exception import CoilsException, AuthenticationException
from coils.foundation import *
from sqlalchemy import *

class Authenticator(object):
    _cache = None
    _hosts = None

    def __init__(self, context, metadata, options):
        self.log = logging.getLogger('authenticator')
        if (Authenticator._cache is None):
            Authenticator._cache = { }
        self.account = None
        self.options = options
        self.db = context.db_session()
        if (self._check_tokens(metadata)):
            return
        if (self._check_trusted_hosts(metadata)):
            return
        elif (metadata['authentication'].has_key('login')):
            self.log.debug('login detected, trying authentication')
            self._authenticate(context, metadata)
        else:
            self.log.debug('No credentials, not attempting authentication')
            raise AuthenticationException('No credentials, not attempting authentication')

    def _authenticate(self, context, metadata):
        ''' Perform token based authentication that should ALWAYS work
            regardless of identification/authentication backend.
            TODO: Implement token based authentication, see OGo/J '''
        # TODO: Check Token Authentication
        cached = self._check_cache_for_account(metadata['authentication']['login'])
        # Currently we only support BASIC (aka PLAIN), but someday....
        if (cached is not None):
            self.log.debug('Found cached credentials for %s' % cached['login'])
            # Caching credentials only works for PLAIN authentication
            if (metadata['authentication']['mechanism'] == 'PLAIN'):
                if (metadata['authentication']['secret'] == cached['secret']):
                    self.log.debug('Authenticated using cached credentials')
                    self.account = cached['account']
                    return True;
        self.account = self._getLogin(metadata['authentication']['login'])
        self.log.debug('retrieved login:{0} objectId#{1} from database'.\
            format(self.account.login, self.account.object_id))
        return False

    def _check_tokens(self, metadata):
        # TODO: Implement
        # How does OGo/J do this?
        self.log.warn("Tokens authentication not implemented.")
        return False

    def _check_trusted_hosts(self, metadata):
        if ('connection' in metadata):
            self.log.debug('Checking for trusted remote host.')
            # Context is for a network connected client
            connection = metadata.get('connection')
            if (Authenticator._hosts is None):
                sd = ServerDefaultsManager()
                Authenticator._hosts = sd.default_as_list('PYTrustedHosts')
            self.log.debug('Client connection from {0}'.format(connection.get('client_address')))
            if ((connection.get('client_address').lower() in Authenticator._hosts) and
                ('claimstobe' in metadata['authentication'])):
                login = metadata['authentication']['claimstobe']
                self.account = self._getLogin(login)
                login = metadata['authentication']['login'] = login
                self.log.debug('trusting connection as login:{0} objectId#{1} from remote'.format(
                    self.account.login,
                    self.account.object_id))
                return True
        return False

    def _check_cache_for_account(self, login):
        if (Authenticator._cache.has_key(login)):
            return Authenticator._cache[login]
        return None

    def _set_cached_credentials(self, extra, metadata):
        if (self.account.login is None):
            self.log.error('Attempt to cache account with null login!')
        else:
            Authenticator._cache[metadata['authentication']['login']] = {
                'login': self.account.login,
                'account': self.account,
                'secret': metadata['authentication']['secret'],
                'extra': extra }

    def _getLogin(self, login):
        query = self.db.query(Contact).filter(and_(Contact.login==login,
                                                   Contact.is_account==1,
                                                   Contact.status!='archived'))
        data = query.all()
        if ( len(data) > 1 ):
            raise AuthenticationException('Multiple accounts match criteria!')
        elif ( len(data) == 0 ):
            self.log.error('No such account as {0}.'.format(login))
            raise AuthenticationException('No such account as {0}.'.format(login))
        return data[0]

    def authenticated_id(self):
        if (self.account is not None):
            return self.account.object_id
        return -1

    def authenticated_login(self):
        if (self.account is not None):
            return self.account.login
        return None
