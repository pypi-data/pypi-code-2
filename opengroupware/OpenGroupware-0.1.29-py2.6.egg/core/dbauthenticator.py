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
from crypt  import crypt


class DBAuthenticator(Authenticator):

    def __init__(self, context, metadata, options):
        Authenticator.__init__(self, context, metadata, options)

    def _authenticate(self, context, metadata):
        if (Authenticator._authenticate(self, context, metadata)):
            return
        secret = self.account.password
        if (secret == crypt(metadata['authentication']['secret'], secret[:2])):
            # TODO: Add a timestamp so cached authorizations expire
            self._set_cached_credentials(None, metadata)
            return True
        else:
            raise AuthenticationException('Incorrect username or password')



