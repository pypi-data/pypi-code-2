"""
Implementation of mod_auth_tkt as Python middleware

This is all junk which doesn't need to be part of the module:

#        'TKTAuthCookieName':     'auth_tkt',
#        'TKTAuthBackArgName':    'back',
#
#        'TKTAuthGuestLogin':     0,
#        'TKTAuthGuestUser':      'guest',
#        'TKTAuthIgnoreIP':       0,
#        'TKTAuthRequireSSL':     0,
#        'TKTAuthCookieSecure':   0,
#
#        # Cookie setter options
#        'TKTAuthTimeout':        2 * 60 * 60,
#        'TKTAuthTimeoutMin':     2 * 60,
#        'TKTAuthTimeoutRefresh': 0.5,

# XXX Need to implement badcookie without template
"""

import logging
import time

from authtkt import AuthTicket
from authtkt import AuthTkt
from httpkit.helper.cookie import set_cookie, delete_cookie, get_cookie
from bn import AttributeDict
from pipestack.pipe import Pipe
from conversionkit import Field
from stringconvert import unicodeToUnicode

log = logging.getLogger(__name__)

class BadTicket(Exception):
    """
    Exception raised when a ticket can't be parsed.  If we get
    far enough to determine what the expected digest should have
    been, expected is set.  This should not be shown by default,
    but can be useful for debugging.
    """
    def __init__(self, msg, expected=None):
        self.expected = expected
        Exception.__init__(self, msg)


class AuthTktPipe(Pipe):

    options = dict(
         secret = Field(
            unicodeToUnicode(),
            missing_error = "The required option '%(name)s.secret' is missing",
            empty_error="The option '%(name)s.secret' cannot be empty",
         )
    )

    def __init__(self, *k, **p):
        Pipe.__init__(self, *k, **p)
        self.cookie_name = 'auth_tkt'
        self.include_ip = True
        self.cookie_params = {}
        self.timeout = None
    
        if self.timeout is not None and self.timeout > \
           int(self.cookie_params.get('expires', -1)):
            self.cookie_params['expires'] = self.timeout
        self.secure = False
        if self.cookie_params.has_key('secure') and \
           bool(self.cookie_params['secure']) == True:
            self.secure = True

    def enter(self, service):
        service[self.name] = AttributeDict()
        cookies = get_cookie(service.environ.get('HTTP_COOKIE', ''))
        cookie_value = ''
        if cookies is not None:
            log.debug("These cookies were found: %s", cookies.keys())
            if cookies.has_key(self.cookie_name):
                cookie_value = cookies[self.cookie_name].value
        else:
            log.debug("No HTTP_COOKIE key found in environ")
        log.debug(
            "Our cookie %r value is therefore %r",
            self.cookie_name, 
            cookie_value
        )
        remote_addr = service.environ.get(
            'HTTP_X_FORWARDED_FOR', 
            service.environ.get('REMOTE_ADDR','0.0.0.0')
        ).split(',')[0]
        log.debug(
            "Remote addr %r, value %r, include_ip %r", 
            remote_addr, 
            cookie_value, 
            self.include_ip
        )
        if cookie_value:
            if not self.include_ip:
                # mod_auth_tkt uses this dummy value when IP is not checked:
                remote_addr = '0.0.0.0'
            try:
                log.debug(
                    "Parsing ticket secret %r, cookie value %r, "
                    "remote address %s", service.app.config[self.name].secret, cookie_value, 
                    remote_addr
                )
                ip = remote_addr
                ticket = cookie_value.strip('"').decode('base64')
                log.debug(
                    "parse_ticket(secret=%r, ticket=%r, ip=%r)", 
                    service.app.config[self.name].secret, 
                    ticket,
                    ip
                )
                digest = ticket[:32]
                try:
                    timestamp = int(ticket[32:40], 16)
                except ValueError, e:
                    raise BadTicket('Timestamp is not a hex integer: %s' % e)
                user_data = None
                try:
                    userid, data = ticket[40:].split('!', 1)
                except ValueError:
                    raise BadTicket('userid is not followed by !')
                if '!' in data:
                    tokens, new_user_data = data.split('!', 1)
                    if user_data is None:
                        user_data = new_user_data
                    tokens = tokens.split(',')
                else:
                    # @@: Is this the right order?
                    tokens = []
                    if user_data is None:
                        user_data = data
                ticket = AuthTicket(
                    service.app.config[self.name].secret, 
                    userid, 
                    ip, 
                    tokens=tokens,
                    user_data=user_data, 
                    time=timestamp,
                    cookie_name=self.cookie_name,
                    secure=self.secure,
                )
                expected = ticket.digest()
                if expected != digest:
                    raise BadTicket(
                        'Digest signature is not correct',
                        expected=(expected, digest)
                    )
            except BadTicket, e:
                if e.expected:
                    log.warning("BadTicket: %s Expected: %s", e, e.expected)
                else:
                    log.warning("BadTicket: %s", e)
                service.environ['authkit.cookie.error'] = True
            else:
                now = time.time()
                log.debug("Time difference: %s", str(now-timestamp))
                log.debug("Cookie params expire: %s", self.timeout)
                if self.timeout and now - timestamp > float(self.timeout)+1:
                    service.environ['authkit.cookie.error'] = True
            service[self.name]['username'] = None
            service[self.name]['data'] = None
            service[self.name]['tokens'] = None
            if not service.environ.get('authkit.cookie.error', False):
                service.environ['REMOTE_USER'] = userid
                if service.environ.get('REMOTE_USER_TOKENS'):
                    # We want to add tokens/roles to what's there:
                    tokens = service.environ['REMOTE_USER_TOKENS'] + tokens
                service.environ['REMOTE_USER_TOKENS'] = tokens
                service.environ['REMOTE_USER_DATA'] = user_data
                service.environ['AUTH_TYPE'] = 'cookie'
                service[self.name]['username'] = userid
                service[self.name]['data'] = user_data
                service[self.name]['tokens'] = tokens
                def logout():
                    service.http_response.header_list.append(
                        dict(
                            name='Set-Cookie',
                            value=delete_cookie(
                                self.cookie_name,
                                path='/',
                            )
                        )
                    )
                service[self.name]['logout'] = logout
            # Remove REMOTE_USER set by any other application.
            elif service.environ.has_key('REMOTE_USER'):
                log.warning(
                    'Removing the existing REMOTE_USER key because of a bad '
                    'cookie'
                )
                del service.environ['REMOTE_USER']
        def sign_in(
            username,
            tokens=['one', 'two', 'three'],
            user_data='User Data',
        ):
            at = AuthTkt(
                conf=service.app.option[self.name]['filename'], 
                secret=service.app.option[self.name]['secret'],
            )
            ip_addr=None
            if not at['ignore_ip']:
                ip_addr = service.environ['REMOTE_ADDR']
            tkt = at.ticket(
                userid=username,
                ip=ip_addr,
                tokens=tokens,
                user_data=user_data,
            )
            value = tkt.cookie_value().encode('base64')
            cookie = set_cookie('auth_tkt', value.strip().replace('\n',''))
            service.http_response.header_list.insert(0, dict(name='Set-Cookie', value=cookie))
            return cookie
        service[self.name]['sign_in'] = sign_in

    def leave(self, service, error=False):
        # Remove the cookie if it is invalid.
        if service.environ.get('authkit.cookie.error', False):
           new_header_list = []
           found = False
           for header in service.http_response.header_list:
               if header['name'].lower() == 'set-cookie':
                   new_header_list.append(dict(name=header['name'], value=header['value'][:-1]+'; '+cookie_name+'="";'))
               else:
                   new_header_list.append(dict(name=name, value=value))
           service.http_response.header_list = new_header_list

