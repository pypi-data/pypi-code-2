# Copyright (c) 2008,2009  Mediamatic Lab
# See LICENSE for details.

import sys

from oauth.oauth import OAuthSignatureMethod, OAuthToken, OAuthConsumer, OAuthRequest, OAuthSignatureMethod_HMAC_SHA1, escape, _utf8_str
import httplib, urllib, simplejson, base64, os
from anymeta import __version__

class APIMethodPart(object):

    api = None
    part = ''

    def __init__(self, api, part):
        self.api = api
        self.part = part

    def __getattr__(self, part):
        return APIMethodPart(self.api, self.part + '.' + part)

    def __call__(self, **kwargs):
        return self.api.doMethod(self.part, kwargs)


class AnyMetaException(Exception):

    code    = None
    message = None

    def __init__(self, code, msg):
        self.code    = code
        self.message = msg
        Exception.__init__(self, "%s: %s" % (code, msg))

    pass


class AnyMetaAPI(object):

    entrypoint = None
    consumer = None
    token = None
    sigmethod = None
    _getPage = None

    last_headers = None
    agent = None

    requestTimeout = 0


    def __init__(self, entrypoint, oauth=None, **args):
        """
        Initializes the AnyMeta API
        """
        self.entrypoint = entrypoint
        self.oauth = oauth
        if oauth:
            self.consumer = OAuthConsumer(oauth['c_key'], oauth['c_sec'])
            self.token = OAuthToken(oauth['t_key'], oauth['t_sec'])
            self.sigmethod = OAuthSignatureMethod_HMAC_SHA1()

        engine = args.get('engine', 'httplib')
        self._getPage = getattr(self, '_getPage_%s' % engine)
        self.agent = args.get('agent', 'AnyMetaAPI/%s (%s; python)' % (__version__, os.uname()[0]))


    @staticmethod
    def from_registry(key, **args):
        """
        Create an AnyMeta instance by looking into the local key registry.
        """
        from registry import AnyMetaRegistry
        registry = AnyMetaRegistry.getInstance()
        r = registry.get(key)
        return AnyMetaAPI(r['entrypoint'], r['oauth'], **args)


    def __getattr__(self, base):
        return APIMethodPart(self, base)


    def exp(self, args):
        return self.__expand_parameters(args)


    def __expand_parameters(self, arg, key = "", prefix = ""):
        """
        Flatten parameters into a URL-compliant array.
        """
        newargs = {}

        if prefix == "":
            nextprefix = "%s"
        else:
            nextprefix = "[%s]"

        if type(arg) == dict:
            for k in arg.keys():
                n = self.__expand_parameters(arg[k], k, nextprefix % k)
                for k2 in n.keys():
                    newargs[prefix+k2] = n[k2]

        elif type(arg) == list:
            for i in range(len(arg)):
                n = self.__expand_parameters(arg[i], str(i), nextprefix % str(i))
                for k in n.keys():
                    newargs[prefix+k] = n[k]
        else:
            if prefix == key:
                nextprefix = "%s"
            newargs[nextprefix % key] = arg

        return newargs


    def __parse_parameters(self, args):
        """
        Convert arguments to AnyMeta compliance.

        This includes some handy magic for uploading files: if a string starts
        with an '@', and it will be considered a file, and replaced by the
        base64 data of the file.
        """
        if type(args) != dict:
            return args

        for k in args.keys():
            if (type(args[k]) == str or type(args[k]) == unicode) \
                   and len(args[k]) > 0 and args[k][0] == "@":

                filename = args[k][1:]
                if filename == os.path.abspath(filename):
                    # only accept absolute paths
                    fp = open(args[k][1:], "r")
                    data = base64.b64encode("".join(fp.readlines()))
                    fp.close()
                    args[k] = data
            elif type(args[k]) == dict:
                args[k] = self.__parse_parameters(args[k])
            elif type(args[k]) == list:
                for i in range(len(args[k])):
                    args[k][i] = self.__parse_parameters(args[k][i])

        return args


    def doMethod(self, method, parameters, http_method="POST", headers=None, data=None, format='json'):
        """
        Call the specified AnyMeta method. Currently, all requests are
        done as POST."""

        parameters = self.__parse_parameters(parameters)

        parameters['method'] = method
        parameters['format'] = format

        parameters = self.__expand_parameters(parameters)

        headers = headers or {}
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.agent

        if self.oauth:
            url, postdata, headers = self._getOAuthRequest(http_method, method, parameters, headers, data)
        else:
            url, postdata, headers = self._getAnonymousRequest(http_method, method, parameters, headers, data)
        return self._getPage(http_method, str(url), postdata, headers, format)


    def _getAnonymousRequest(self, http_method, method, parameters, headers, data):

        encodedParameters = '&'.join(['%s=%s' % (escape(_utf8_str(k)),
                                                 escape(_utf8_str(v)))
                                      for k, v in parameters.iteritems()])
        url = "%s?%s" % (self.entrypoint, encodedParameters)
        return url, data, headers


    def _getOAuthRequest(self, http_method, method, parameters, headers, data):
        request = OAuthRequest.from_consumer_and_token(self.consumer,
                                                       token=self.token,
                                                       http_method=http_method,
                                                       http_url=self.entrypoint,
                                                       parameters=parameters)
        request.sign_request(self.sigmethod, self.consumer, self.token)

        if data is None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            url = self.entrypoint
            postdata = '&'.join(['%s=%s' % (escape(_utf8_str(k)),
                                            escape(_utf8_str(v))) \
                                 for k, v in request.parameters.iteritems()])

        else:
            encodedParameters = '&'.join(['%s=%s' % (escape(_utf8_str(k)),
                                                     escape(_utf8_str(v)))
                                          for k, v in parameters.iteritems()
                                          if not k.startswith('oauth_')])
            url = "%s?%s" % (self.entrypoint, encodedParameters)
            postdata = data
            headers.update(request.to_header())
        return url, postdata, headers


    def _processPage(self, page, format):
        if format != 'json':
            return page

        try:
            result = simplejson.loads(unicode(page))
        except ValueError, e:
            raise AnyMetaException(0, "API error: %s\n\n%s" % (e, page))

        if type(result) == dict and 'err' in result:
            err = result['err']['-attrib-']
            raise AnyMetaException(err['code'], err['msg'])

        return result


    def _getPage_httplib(self, http_method, url, body, headers, format):
        host = urllib.splithost(urllib.splittype(url)[1])[0]

        if sys.version_info >= (2,6) and self.requestTimeout > 0:
            conn = httplib.HTTPConnection(host, timeout=self.requestTimeout)
        else:
            conn = httplib.HTTPConnection(host)

        conn.request(http_method, url, body=body, headers=headers)

        response = conn.getresponse()

        self.last_headers = dict(response.getheaders())

        page = response.read()
        return self._processPage(page, format)


    def _getPage_twisted(self, http_method, url, body, headers, format):
        from twisted.web import client

        d = client.getPage(url, method=http_method, postdata=body, timeout=self.requestTimeout,
                           headers=headers, agent=self.agent)
        d.addCallback(self._processPage, format)
        return d
