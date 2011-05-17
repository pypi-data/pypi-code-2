#!/usr/bin/env python
import urllib2
import socket
import cookielib
import logging

from tools.net import headers

socket.setdefaulttimeout(5)


class Browser(object):
    """
    Simple wrapper around urllib2 which emulates web browser.
    """

    def __init__(self, log_file=None):
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),
                                           urllib2.HTTPSHandler())
        self.referer = None
        self.headers = headers.random_request()
        self.log_file = log_file

    def request(self, url, referer=None, proxy=None, random_headers=False):
        if random_headers:
            self.headers = headers.random_request()
        req = urllib2.Request(url)
        if proxy:
            req.set_proxy(proxy, 'http')
        if referer or self.referer:
            req.add_header('Referer', referer if referer else self.referer)
        for name, value in self.headers.items():
            req.add_header(name, value)
        logging.debug('Retreiving %s' % url)
        self.response = self.opener.open(req)
        self.referer = self.response.geturl()
        body = self.response.read()
        if self.log_file:
            open(self.log_file, 'w').write(body)
        return body
