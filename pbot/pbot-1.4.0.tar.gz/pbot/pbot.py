#!/usr/bin/env python
# vim:fileencoding=utf-8
# ---------------------------------------
# Robot for parsing, crawlig sites
# Author: Pavel Zhukov (gelios@gmail.com)
# ---------------------------------------

__version__ = '1.1.0'
__author__ = 'Pavel Zhukov (gelios@gmail.com)'

import urllib
import urllib2

from cookielib import CookieJar, Cookie
import logging
from copy import copy

BASIC_HEADERS = {
    'User-Agent':    'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7 GTB5',
    'Accept':       'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language':    'ru,en-us;q=0.7,en;q=0.3',
    'Accept-Encoding':    'deflate',
    'Accept-Charset':    'windows-1251,utf-8;q=0.7,*;q=0.7',
}
RHEADERS = [BASIC_HEADERS]

class ImpropertlyConfigured(Exception):
    pass


def force_unicode(values, encoding):
#Convert values to unicode if it's not unicode
    if hasattr(values, 'items'):
        #This is a dict
        values = [(k, v) for k, v in values.items()]
    encoded_values = []
    for k, v in values:
        if isinstance(k, unicode):
            k = k.encode(encoding)
        if isinstance(v, unicode):
            v = v.encode(encoding)
        encoded_values.append((k, v))
    return encoded_values

class Bot(object):
    '''
    Basic HTTP crawler builded against urllib/urllib2
    This is just a current state storage (cookie and referral that can be used for crawling)
    '''

    def __init__(self, send_referral=True, parse_cookies=True, proxies=None, cookiejar=None, add_headers=None,
                 encoding='utf-8', debug=False):
        '''
        Set basic headers settings
        '''
        self.headers = BASIC_HEADERS
        self.send_referral = send_referral
        self.parse_cookies = parse_cookies
        self.proxies = proxies
        if cookiejar is None:
            self.cj = CookieJar()
        self.browser = None
        self._add_headers = add_headers or {}
        self.current_url = None
        self.encoding = encoding
        self.debug = debug

    def refresh_connector(self):
        '''
        Reinitialize Cookies and Headers
        '''
        self.cj = CookieJar()
        self.headers = BASIC_HEADERS
        self.headers.update(self._add_headers)
        self._create_connector()
        self.current_url = None

    def _create_connector(self):
        '''
        Create new OpenerDirector object using selected parameters
        '''
        if self.debug:
            h = urllib2.HTTPHandler(debuglevel=1)
        else:
            h = urllib2.HTTPHandler()
        if self.proxies:
            proxy_handler = urllib2.ProxyHandler(self.proxies)
            self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), proxy_handler, h)
        else:
            self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), h)
        self.browser.addheaders = self.headers.items()

    def open(self, url, post=None, get=None, referrer=None, ):
        '''
        Open target url
        Drop previous refferer
        Save cookies
        Encode get and post values to self.encoding
        '''
        if self.browser is None:
            self._create_connector()
        target = url
        #Remove referrer if exists
        if referrer:
            self.headers['Referrer'] = referrer
        elif 'Referrer' in self.headers:
            del self.headers['Referrer']
        self.browser.add_headers = self.headers
        if get:
            get = force_unicode(get, self.encoding)
            target = url + '?' + urllib.urlencode(get)
        logging.debug('url: %s' % target)
        logging.debug('headers %s' % self.headers)
        logging.debug('post: %s' % post)
        logging.debug('referrer: %s' % referrer)
        if post:
            post = force_unicode(post, self.encoding)
            post = urllib.urlencode(post)
            logging.debug(post)
            self.response = self.browser.open(target, post)
        else:
            self.response = self.browser.open(target)
        self.current_url = target
        return self.response

    def follow(self, url, post=None, get=None):
        self.open(url, post=post, get=get, referrer=self.current_url)
        return self.response

    def open_http(self, method, url, values):
        '''
        Specically for lxml submit_form
        '''
        if method == 'GET':
            return self.follow(url, get=values)
        elif method == 'POST':
            return self.follow(url, post=values)
        else:
            raise ValueError('method parametr in bot.open_http should be eiser GET or POST')

    def add_cookie(self, **kwargs):
        '''
        Add a Cookie to CookieJar used by OpenerDirector
        You can specify any Cookie params, not-specified params will be setted by default
        '''
        default_cookie = {
            'version': 0,
            'name': 'name',
            'value': '1',
            'port': None,
            'port_specified': False,
            'domain': 'www.example.com',
            'domain_specified': False,
            'domain_initial_dot': False,
            'path': '/',
            'path_specified': True,
            'secure': False,
            'expires': None,
            'discard': True,
            'comment': None,
            'comment_url': None,
            'rest': {'HttpOnly': None},
            'rfc2109': False
        }
        default_cookie.update(kwargs)
        self.cj.set_cookie(Cookie(**default_cookie))

    def clone(self):
        ''' Shortcut for copy '''
        return copy(self)
