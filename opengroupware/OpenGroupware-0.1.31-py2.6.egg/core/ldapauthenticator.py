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
from authenticator import Authenticator
from exception import CoilsException, AuthenticationException
from coils.foundation import Session, Contact
import ldap, ldap.sasl
import ldaphelper

class LDAPAuthenticator(Authenticator):
    _dsa = None

    def __init__(self, context, metadata, options):
        self._verify_options(options)
        Authenticator.__init__(self, context, metadata, options)

    def _verify_options(self, options):
        #TODO: Check the options to make sure we have function values
        return

    def _bind_and_search(self, options, login):
        # Bind to the DSA and search for the user's DN
        dsa = ldap.initialize(options['url'])
        if (options['start_tls'] == 'YES'):
            dsa.start_tls_s()
        if (options['binding'] == 'SIMPLE'):
            dsa.simple_bind_s(options['bind_identity'],
                              options['bind_secret'])
        elif (options['binding'] == 'DIGEST'):
            tokens = ldap.sasl.digest_md5(options['bind_identity'],
                                          options['bind_secret'])
            dsa.sasl_interactive_bind_s("", tokens)
            self._search_bind()
        result = dsa.search_s(options["search_container"],
                              ldap.SCOPE_SUBTREE,
                               options["search_filter"] % login,
                              [ options["uid_attribute"] ])
        return ldaphelper.get_search_results( result )


    def _test_simple_bind(self, options, dn, secret):
        dsa = ldap.initialize(options['url'])
        if (options['start_tls'] == 'YES'):
            LDAPAuthenticator._dsa.start_tls_s()
        result = False
        try:
            dsa.simple_bind_s(dn, secret)
            result = True
            dsa.unbind()
        except Exception, e:
            self.log.exception(e)
        return result

    def _authenticate(self, context, metadata):
        if (Authenticator._authenticate(self, context, metadata)):
            return
        if (self.options['binding'] == 'SIMPLE'):
            accounts = self._bind_and_search(self.options, metadata['authentication']['login'])
            if (len(accounts) == 0):
                raise AuthenticationException('Matching account not returned by DSA')
            elif (len(accounts) > 1):
                raise AuthenticationException('Dupllicate accounts returned by DSA')
            else:
                # Only one found
                dn = accounts[0].get_dn()
                if (dn is None):
                    self.log.warn('LDAP object with null DN!')
            if (self._test_simple_bind(self.options, dn, metadata['authentication']['secret'])):
                self.log.debug('LDAP bind with {0}'.format(dn))
                self._set_cached_credentials({'dn': dn}, metadata)
                return
            else:
                raise AuthenticationException('DSA declined username or password')
        elif (self.options['binding'] == 'SASL'):
            # TODO Implement LDAP SASL bind test
            raise AuthenticationException('SASL bind test not implemented!')
        raise AuthenticationException('Incorrect username or password')
