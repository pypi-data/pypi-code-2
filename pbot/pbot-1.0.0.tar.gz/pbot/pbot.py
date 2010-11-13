#!/usr/bin/env python
# vim:fileencoding=utf-8
# ---------------------------------------
# Robot for parsing, crawlig sites
# Author: Pavel Zhukov (gelios@gmail.com)
# ---------------------------------------
import urllib
import urllib2
from cookielib import CookieJar
import logging

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

class Bot(object):
    '''
    Basic HTTP crawler builded against urllib/urllib2
    This is just a current state storage (cookie, referral that can be used for crawling
    '''

    def __init__(self, send_referral=True, parse_cookies=True, proxies=None, cookiejar=None, add_headers=None):
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
        self._add_headers = add_headers
        self.current_url = None

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
        if self.proxies:
            proxy_handler = urllib2.ProxyHandler(self.proxies)
            self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), proxy_handler)
        else:
            self.browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.browser.add_headers = self.headers

    def open(self, url, post=None, get=None, referrer=None, ):
        '''
        Open target url
        Drop previous refferer
        Save cookies
        '''
        if self.browser is None:
            self.refresh_connector()
        target = url
        #Remove referrer if exists
        if referrer:
            self.headers['Referrer'] = referrer
        elif 'Referrer' in self.headers:
            del self.headers['Referrer']
        self.browser.add_headers = self.headers
        if get:
            target = url + '?' + urllib.urlencode(get)
        logging.debug('url: %s' % target)
        logging.debug('headers %s' % self.headers)
        logging.debug('post: %s' % post)
        logging.debug('referrer: %s' % referrer)
        if post:
            self.response = self.browser.open(target, urllib.urlencode(post))
        else:
            self.response = self.browser.open(target)
        self._current_url = target
        return self.response

    def follow(self, url, post=None, get=None):
        self.response = self.open(url, post=post, get=get, referrer=self._current_url)
        return self.response

    def open_http(self, method, url, values):
        '''
        Specically for lxml submit_form
        '''
        if method == 'GET':
            self.follow(url, get=values)
        elif method == 'POST':
            self.follow(url, post=values)
        else:
            raise ValueError('method parametr in bot.open_http should be eiser GET or POST')

