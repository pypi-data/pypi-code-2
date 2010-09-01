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
from httpkit.helper.cookie import get_cookie, delete_cookie
from bn import AttributeDict

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

class Self(object): pass

def authTktService(
    cookie_name='auth_tkt',
    ignore_ip=False,
    cookie_params=None,
    timeout=None,
):
    self = Self()

    self.cookie_name = cookie_name
    self.include_ip = not bool(ignore_ip)
    self.cookie_params = cookie_params and cookie_params.copy() or {}
    self.timeout = timeout
    if self.timeout is not None and self.timeout > \
       int(self.cookie_params.get('expires', -1)):
        self.cookie_params['expires'] = self.timeout
    self.secure = False
    if self.cookie_params.has_key('secure') and \
       bool(self.cookie_params['secure']) == True:
        self.secure = True

    def authTktService_constructor(service, name, *k, **p):

        from configconvert import handle_option_error, handle_section_error
        if not service.app.option.has_key(name):
            raise handle_section_error(service, name, "'%s.secret'"%(name))
        from conversionkit import Conversion
        from stringconvert import unicodeToUnicode
        from recordconvert import toRecord

        to_unicode = unicodeToUnicode()
        converter = toRecord(
             missing_errors = dict(
                 secret = "The required option '%s.secret' is missing" % (name,),
             ),
             empty_errors = dict(
                 secret="The option '%s.secret' cannot be empty"%(name,),
             ),
             converters = dict(
                 secret = to_unicode,
             )
        )
        conversion = Conversion(service.app.option[name]).perform(converter)
        if not conversion.successful:
            handle_option_error(conversion, name)
        else:
            service.app.config[name] = conversion.result

        def start(service):
            service[name] = AttributeDict()
            cookies = get_cookie(service.http.environ.get('HTTP_COOKIE', ''))
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
            remote_addr = service.http.environ.get(
                'HTTP_X_FORWARDED_FOR', 
                service.http.environ.get('REMOTE_ADDR','0.0.0.0')
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
                        "remote address %s", service.app.config[name].secret, cookie_value, 
                        remote_addr
                    )
                    ip = remote_addr
                    ticket = cookie_value.strip('"').decode('base64')
                    log.debug(
                        "parse_ticket(secret=%r, ticket=%r, ip=%r)", 
                        service.app.config[name].secret, 
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
                        service.app.config[name].secret, 
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
                    service.http.environ['authkit.cookie.error'] = True
                else:
                    now = time.time()
                    log.debug("Time difference: %s", str(now-timestamp))
                    log.debug("Cookie params expire: %s", self.timeout)
                    if self.timeout and now - timestamp > float(self.timeout)+1:
                        service.http.environ['authkit.cookie.error'] = True
                service[name]['username'] = None
                service[name]['data'] = None
                service[name]['tokens'] = None
                if not service.http.environ.get('authkit.cookie.error', False):
                    service.http.environ['REMOTE_USER'] = userid
                    if service.http.environ.get('REMOTE_USER_TOKENS'):
                        # We want to add tokens/roles to what's there:
                        tokens = service.http.environ['REMOTE_USER_TOKENS'] + tokens
                    service.http.environ['REMOTE_USER_TOKENS'] = tokens
                    service.http.environ['REMOTE_USER_DATA'] = user_data
                    service.http.environ['AUTH_TYPE'] = 'cookie'
                    service[name]['username'] = userid
                    service[name]['data'] = user_data
                    service[name]['tokens'] = tokens
                    def logout():
                        service.http.response.headers.append(
                            (
                                'Set-Cookie',
                                delete_cookie(
                                    self.cookie_name,
                                    path='/',
                                )
                            )
                        )
                    service[name]['logout'] = logout
                # Remove REMOTE_USER set by any other application.
                elif service.http.environ.has_key('REMOTE_USER'):
                    log.warning(
                        'Removing the existing REMOTE_USER key because of a bad '
                        'cookie'
                    )
                    del service.http.environ['REMOTE_USER']
    
        def stop(service, error):
            # Remove the cookie if it is invalid.
            if service.http.environ.get('authkit.cookie.error', False):
               new_headers = []
               found = False
               for name, value in service.http.response.headers:
                   if name.lower() == 'set-cookie':
                       new_headers.append((name, value[:-1]+'; '+cookie_name+'="";'))
                   else:
                       new_headers.append((name, value))
               service.http.response.headers = new_headers

        return AttributeDict(enter=start, leave=stop) 
    return authTktService_constructor

AuthTktPipe = authTktService()
