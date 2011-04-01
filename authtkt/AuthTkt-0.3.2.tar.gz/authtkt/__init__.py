# -*- charset: utf-8 -*-

"""\
An implementation of the authentication features required to work with
mod_auth_tkt from Python.

This is basically a port of all the Perl functionality and examples contained
in mod_auth_tkt.

.. note ::

    This code all looks a bit of a mess from a Python progammers point of 
    view but I've tried hard to keep the implemenation here as close as 
    possible to the original Perl version so that any changes to that 
    version can be easily ported back to this version. As a result the
    code isn't written in the way I would normally write this sort of 
    module but on this occassion I judged maintainability to be more 
    important than style.

"""

############################################################################
#
# Apache Configuration Parsing 
#
# This section implements the Perl ``Apache::AuthTkt`` code 
#

# It would be more sensible if mod_auth_tkt passed the configuration via an
# environment variable but it doesn't so we have to parse the configuration
# manually, which means strucutring a virtual host so that all the AuthTkt
# options are ``include``d from thier own file an parsed like with this parser.

import sys
import re
import logging 
import datetime

log = logging.getLogger('auth_tkt')

# Now from the options, generate
PREFIX = 'TKTAuth'
DEFAULTS = {
    'TKTAuthCookieName':     'auth_tkt',
    'TKTAuthBackArgName':    'back',
    'TKTAuthTimeout':        2 * 60 * 60,
    'TKTAuthTimeoutMin':     2 * 60,
    'TKTAuthTimeoutRefresh': 0.5,
    'TKTAuthGuestLogin':     0,
    'TKTAuthGuestUser':      'guest',
    'TKTAuthIgnoreIP':       0,
    'TKTAuthRequireSSL':     0,
    'TKTAuthCookieSecure':   0,
}

def parse_conf(filename, DEFAULTS=DEFAULTS, PREFIX=PREFIX, ignore_secret=False):
    config = {}
    config_file = open(filename, 'r')
    for line in config_file:
        # Get rid of \n
        line = line.strip()
        # Empty?
        if not line:
            continue
        if line.startswith("#") or line.startswith('<'):
            continue
        parts = line.split(" ")
        name = parts[0]
        value = ' '.join(parts[1:])
        # Strip leading " characters.
        if (value[0] == value[-1] == '"') and len(value)>1:
            value = value[1:-1]
        name = name.strip()
        if name.startswith(PREFIX) and not config.has_key('name'):
            log.debug("Found %r %r", name, value)
            config[name] = value
    config_file.close() 

    # Merge in defaults
    d = DEFAULTS.copy()
    d.update(config)
    config = d

    if not config.has_key('TKTAuthSecret') and not ignore_secret:
        raise Exception(
            'TKTAuthSecret directive not found in config file %r'%filename
        )

    # The perl implementation obtains this from the environment HTTP_HOST or SERVER_NAME
    # but to me that defeats the object of having it surely?
    #if not config.has_key('TKTAuthDomain'):
    #    raise Exception('TKTAuthDomain directive not found')

    final = {}
    config_map = {
        'secret':            'Secret',
        'cookie_name':       'CookieName',
        'back_cookie_name':  'BackCookieName',
        'back_arg_name':     'BackArgName',
        'domain':            'Domain',
        'cookie_expires':    'CookieExpires',
        'login_url':         'LoginURL',
        'timeout_url':       'TimeoutURL',
        'post_timeout_url':  'PostTimeoutURL',
        'unauth_url':        'UnauthURL',
        'timeout':           'Timeout',
        'timeout_min':       'TimeoutMin',
        'timeout_refresh':   'TimeoutRefresh',
        'token':             'Token',
        'debug':             'Debug',
        'guest_login':       'GuestLogin',
        'guest_user':        'GuestUser',
        'ignore_ip':         'IgnoreIP',
        'require_ssl':       'RequireSSL',
        'cookie_secure':     'CookieSecure',
    }
    convert = {}
    for k, v in config_map.items():
        convert[v] = k 
    for k, v in config.items():
        name = k[len(PREFIX):]
        if k in ['TKTAuthGuestLogin', 'TKTAuthIgnoreIP', 'TKTAuthRequireSSL', 'TKTAuthCookieSecure']:
            value = {'0': 0, '1': 1, 'on':1, 'yes':1, 'true':1, 'off':0, 'no':0, 'false':0}[str(v).lower()]
        elif k in ['TKTAuthCookieExpires', 'TKTAuthTimeout']:
            value = convert_time_seconds(v)
        elif name in config_map.values():
            value = v
        else:
            raise Exception('Unknown directive %r (%r)'%(k, name))


        # No idea why we can't allow the AuthTktDebug setting in the final dictionary but that is
        # what happens in the original.
        if convert[name] != 'debug':
            final[convert[name]] = value
    final['conf'] = filename
    final['debug'] = 0
    return final

def convert_time_seconds(time):
    # Helper routine to convert time units into seconds
    units = { 
      's' : 1,
      'm' : 60,
      'h' : 3600,
      'd' : 86400,
      'w' : 7 * 86400,
      'M' : 30 * 86400,
      'y' : 365 * 86400,
    }
    try:
        return int(time)
    except (ValueError, TypeError), e:
        sec = 0
        mode = 'number'
        amt = ''
        time = time.replace(' ','')
        for i in range(len(time)):
            if time[i] in units.keys():
                if not amt:
                    raise Exception('Expected a number before %r in %r'%(time[i], time))
                else:
                    sec += int(amt) * units[time[i]]
                    amt = ''
            else:
                amt += time[i]
        if amt:
            sec += int(amt) * units[time[i]]
        return datetime.timedelta(seconds=sec)

# We are re-using the contributes AuthTicket rather than creating our own implementation.
# Start contributed code ----->

##########################################################################
#
# Copyright (c) 2005 Imaginary Landscape LLC and Contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################

import time as time_mod
import cgi
import Cookie
from hashlib import md5

class AuthTicket(object):

    """
    This class represents an authentication token.  You must pass in
    the shared secret, the userid, and the IP address.  Optionally you
    can include tokens (a list of strings, representing role names),
    'user_data', which is arbitrary data available for your own use in
    later scripts.  Lastly, you can override the cookie name and
    timestamp.

    Once you provide all the arguments, use .cookie_value() to
    generate the appropriate authentication ticket.  .cookie()
    generates a Cookie object, the str() of which is the complete
    cookie header to be sent.

    CGI usage::

        token = auth_ticket.AuthTicket('sharedsecret', 'username',
            os.environ['REMOTE_ADDR'], tokens=['admin'])
        print 'Status: 200 OK'
        print 'Content-type: text/html'
        print token.cookie()
        print
        ... redirect HTML ...

    Webware usage::

        token = auth_ticket.AuthTicket('sharedsecret', 'username',
            self.request().environ()['REMOTE_ADDR'], tokens=['admin'])
        self.response().setCookie('auth_tkt', token.cookie_value())

    Be careful not to do an HTTP redirect after login; use meta
    refresh or Javascript -- some browsers have bugs where cookies
    aren't saved when set on a redirect.
    """

    def __init__(self, secret, userid, ip, tokens=(), user_data='',
                 time=None, cookie_name='auth_tkt',
                 secure=False):
        self.secret = secret
        self.userid = userid
        self.ip = ip
        self.tokens = ','.join(tokens)
        self.user_data = user_data
        if time is None:
            self.time = time_mod.time()
        else:
            self.time = time
        self.cookie_name = cookie_name
        self.secure = secure

    def ipts(self):
        ip_chars = ''.join(map(chr, map(int, self.ip.split('.'))))
        t = int(self.time)
        ts = ((t & 0xff000000) >> 24,
              (t & 0xff0000) >> 16,
              (t & 0xff00) >> 8,
              t & 0xff)
        ts_chars = ''.join(map(chr, ts))
        return ip_chars + ts_chars

    def digest0(self):
        log.debug('%r %r %r %r %r', self.ipts(), str(self.secret), str(self.userid), str(self.tokens), str(self.user_data))
        return md5(
            self.ipts() + str(self.secret)
            + str(self.userid) + '\0' + str(self.tokens)
            + '\0' + str(self.user_data)).hexdigest()

    def digest(self):
        log.debug('%r %r', self.digest0(), str(self.secret))
        return md5(self.digest0() + self.secret).hexdigest()

    def cookie_value(self):
        v = '%s%08x%s!' % (self.digest(), int(self.time), self.userid)
        if self.tokens:
            v += self.tokens + '!'
        v += self.user_data
        return v

    def cookie(self):
        c = Cookie.SimpleCookie()
        c[self.cookie_name] = self.cookie_value().encode('base64').strip()
        c[self.cookie_name]['path'] = '/'
        if self.secure:
            c[self.cookie_name]['secure'] = 'true'
        return c

# <----- End contributed code 

# Now we need a class to store the variables and wrap the ticket parsing

class AuthTkt(object):
    """\

    Parse an Apache config file conating the mod_auth_tkt options and provide
    a dictionary-like interface to read them.

    Also provide a ``ticket()`` method to generate a ticket based on the 
    options.

    .. note ::

        This class is designed to be a close approximation to the functionality
        contained in the Perl ``AuthTkt.pm`` module at
        http://search.cpan.org/~gavinc/Apache-AuthTkt-0.08/AuthTkt.pm and is the
        main interface which should be used in an implementation to access the
        AuthTkt* options and generate tickets.

    Used it like this::

        # Constructor - either (preferred):
        at = AuthTkt(conf='/etc/httpd/conf.d/auth_tkt.conf')
        # OR:
        at = AuthTkt(secret='818f9c9d-91ed-4b74-9f48-ff99cfe00a0e')

        # Generate ticket
        ticket = at.ticket(userid=username, ip=ip_addr)
    
        # Get the ticket cookie value:
        value = ticket.cookie_value()

        # Or generate cookie containing ticket
        cookie = ticket.cookie()
    
        # Access the shared secret
        secret = at['secret']
        # If using the 'conf' constructor above, all other TKTAuth attributes 
        #   are also available e.g.:
        at['cookie_name'], at['ignore_ip'], at['request_ssl']

    """
    def __init__(self, conf=None, secret=None):
        if conf is None and secret is None:
            raise Exception('You must specify a config file or secret')
        if conf is not None:
            # This adds the filename itself as the ``conf`` key as well as
            # parsing all the variables.
            self.options = parse_conf(conf, DEFAULTS=DEFAULTS, PREFIX=PREFIX, ignore_secret = secret is not None and True)
        if secret is not None:
            self.options['secret'] = secret

    def __getitem__(self, name):
        if self.options.has_key(name):
            return self.options[name]
        else:
            raise KeyError('No such option %r'%name)

    def get(self, name, default=None):
        if self.options.has_key(name):
            return self.options[name]
        else:
            return default

    def has_key(self, name):
        return self.options.has_key(name)

    def ticket(self, userid, ip, tokens=(), user_data='', time=None):
        if self['ignore_ip']:
            ip = '0.0.0.0'
        return AuthTicket(
            secret=self['secret'],
            userid=userid,
            ip = ip,
            tokens = tokens,
            user_data = user_data,
            time=time,
            cookie_name = self['cookie_name'],
            secure=self['cookie_secure'],
        )
        
    def cookie(self):
        raise NotImplementedError('Just call ticket().cookie() instead')

