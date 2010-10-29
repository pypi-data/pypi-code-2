# -*- coding: utf-8 -*-

import twisted.web.client as webclient
from twisted.internet import defer, reactor
from simplejson import loads as json_loads, dumps as json_dumps
import base64
import logging

log = logging.getLogger("mekk.nozbe")

PRODUCTION_URL = "http://www.nozbe.com"
DEVEL_URL = "http://devl.nozbe.net"
TIMEOUT = 10 * 60

class NozbeCallException(Exception):
    pass

class NozbeKeyLoadException(NozbeCallException):
    pass

class NozbeConnection(object):
    """
    Low-level HTTP requests handling
    """

    def __init__(self, api_key = None, devel = None, timeout = None):
        """
        Initializes connection-handling object

        @param api_key Nozbe API key. If not specified here, must be
               provided via set_api_key or load_api_key later,
               otherwise most requests will fail

        @param devel if specified, means Nozbe development server
               should be used instead of production. In such a case
               it should be a dictionary 
               { 'user': .... ,  'password' : ... }
               specifying HTTP authentiation for Nozbe development server
               (note also that different api_key must be used in such a case)

        @param timeout request timeout (if default 60 secs is no appropriate)

        """
        if not devel:
            self.url = PRODUCTION_URL
            self.headers = {}
        else:
            self.url = DEVEL_URL
            assert(type(devel) == dict)
            basic_auth = base64.encodestring('%(user)s:%(password)s' % devel)
            auth_header = "Basic " + basic_auth.strip()
            self.headers = dict(Authorization = auth_header)
        self.timeout = timeout
        self.api_key = api_key

    def set_api_key(self, api_key):
        self.api_key = api_key

    @defer.inlineCallbacks
    def load_api_key(self, user, password):
        """
        Uses username and password to grab api key. Saves it and also returns
        """
        reply = yield self.get_request(
            "api", "login", email = user, password = password)
        if not reply:
            raise NozbeCallException("Can not load data from Nozbe. Wrong user/password key?")
        self.api_key = reply['key']
        if not self.api_key:
            raise NozbeKeyLoadException("Invalid username or password")
        defer.returnValue(self.api_key)

    @defer.inlineCallbacks
    def get_request(self, api_url, *call_items, **params):
        """
        Low-level Nozbe call (GET)

        @param call_items: urlpath parts (projects, context, actions, what-context, ...)
        @param args: named GET params
        """
        url = self._make_url(api_url, *call_items, **params)
        log.debug("Getting " + url)
        reply = yield self._get_page(url, headers = self.headers)
        if not reply:
            raise NozbeCallException("Can not load data from Nozbe. Wrong/missing API key?")
        log.debug("Reply: " + reply)
        data = json_loads(reply)
        if (type(data) is dict) and ('error' in data):
            raise NozbeCallException("Nozbe error: %s" % data['error'])
        defer.returnValue(data)

    @defer.inlineCallbacks
    def post_request(self, api_url, *call_items, **params):
        """
        Low-level Nozbe call (POST)

        Note: POST param (dictionary) required, apart from that works like
        _make_get_request.
        """
        post_text = json_dumps(params['POST'])
        del params['POST']
        url = self._make_url(api_url, *call_items, **params)
        log.debug("Posting " + url + " with " + post_text)
        reply = yield self._get_page(url, headers = self.headers, 
                                     method = "POST", postdata = post_text)
        if not reply:
            raise NozbeCallException("Can not save data to Nozbe. Wrong/missing API key?")
        log.debug("Reply: " + reply)
        data = json_loads(reply)
        if (type(data) is dict) and ('error' in data):
            raise NozbeCallException("Nozbe error: %s" % data['error'])
        defer.returnValue(data)

    def _make_url(self, api_url, *call_items, **params):
        parts = [self.url, api_url] + list(call_items) \
            + [ ("%s-%s" % (key, value)) for key, value in params.iteritems() ]
        if self.api_key:
            parts.append("key-%s" % self.api_key)
        url = "/".join(parts)
        if type(url) == unicode:
            url = url.encode("utf-8")
        return url
    
    def _get_page(self, url, *args, **kwargs):
        if self.timeout:
            kwargs['timeout'] = self.timeout
        return NozbeConnection.get_page(url, *args, **kwargs)

    @staticmethod
    def get_page(url, contextFactory=None, *args, **kwargs):
        """
        twisted.web.client.getPage modified to handle timeouts (timeout arg)
        """
        scheme, host, port, path = webclient._parse(url)
        factory = webclient.HTTPClientFactory(url, *args, **kwargs)
        timeout = kwargs.get('timeout', TIMEOUT)
        if scheme == 'https':
            from twisted.internet import ssl
            if contextFactory is None:
                contextFactory = webclient.ssl.ClientContextFactory()
            reactor.connectSSL(host, port, factory, contextFactory, timeout = timeout)
        else:
            reactor.connectTCP(host, port, factory, timeout = timeout)
        return factory.deferred

 
