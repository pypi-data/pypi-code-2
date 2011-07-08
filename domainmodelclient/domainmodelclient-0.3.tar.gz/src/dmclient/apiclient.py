import os, urllib, urllib2, re

try: # Since Python 2.6.
    import json
except ImportError:
    import simplejson as json


class ContentTypeError(Exception): pass

class ApiClient(object):

    apiKeyHeaderName = None
    resourcePaths = {}

    def __init__(self, baseUrl, apiKey=None, isVerbose=False, httpUser=None, httpPass=None, logger=None):
        if self.apiKeyHeaderName == None:
            raise Exception, "Attribute 'apiKeyHeaderName' not set on %s" % self.__class__
        self.baseUrl = baseUrl
        self.apiKey = apiKey
        self.isVerbose = isVerbose
        if httpUser and httpPass:
            manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            manager.add_password(None, baseUrl, httpUser, httpPass)
            handler = urllib2.HTTPBasicAuthHandler(manager)
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)
        self.logger = logger

    def getRegister(self, resourceName):
        url = self.getUrl(resourceName)
        return self.createResponse(url)

    def postRegister(self, resourceName, data):
        url = self.getUrl()
        return self.createResponse(url, data)

    def getEntity(self, resourceName, entityRef):
        url = self.getUrl(resourceName, entityRef)
        return self.createResponse(url)

    def putEntity(self, resourceName, entityRef, data):
        url = self.getUrl(resourceName, entityRef)
        return self.createResponse(url, data)

    def getUrl(self, resourceName, *args):
        path = self.baseUrl
        path += self.resourcePaths[resourceName]
        path %= args
        return path

    def createResponse(self, url, data=None):
        self.lastStatus = None
        self.lastBody = None
        self.lastHeaders = None
        self.lastMessage = None
        self.lastHttpError = None
        self.lastUrlError = None
        self.lastContentType = None
        self.lastUrl = url
        self.log("Opening %s ..." % url)
        try:
            headers = {}
            if data is not None:
                data = self.jsonDumps(data)
                data = urllib.urlencode({data: 1})
                headers[self.apiKeyHeaderName] = self.apiKey
            httpRequest = urllib2.Request(url, data, headers)
            self.httpResponse = urllib2.urlopen(httpRequest)
        except urllib2.HTTPError, inst:
            self.logHttpError(url, headers, data, inst)
            self.lastHttpError = inst
            self.lastStatus = inst.code
            self.lastMessage = inst.read()
        except urllib2.URLError, inst:
            self.logUrlError(url, headers, data, inst)
            self.lastUrlError = inst
            self.lastStatus = inst.reason[0]
            self.lastMessage = inst.reason[1]
        else:
            self.log("OK opening resource at: %s" % url)
            self.lastStatus = self.httpResponse.code
            self.lastBody = self.httpResponse.read()
            self.lastHeaders = self.httpResponse.headers
            self.lastContentType = self.lastHeaders['Content-Type']
            if self.lastContentType == 'application/json':
                self.lastMessage = self.jsonLoads(self.lastBody)
            else:
                self.lastMessage = self.lastBody
                msg = "Resource at %s returned content type '%s'" % (
                    self.lastUrl, self.lastContentType)
                msg += " (application/json was expected)."
                raise ContentTypeError, msg
            self.logLastStatusBodyHeadersMessageContentType()
        return self.lastMessage

    def logHttpError(self, url, headers, data, inst):
        self.log("Received HTTP error code from Quant resource.")
        self.logUrlHeadersDataInst(self, url, headers, data, inst)

    def logUrlError(self, url, headers, data, inst):
        self.log("Unable to progress with URL.")
        self.logUrlHeadersDataInst(self, url, headers, data, inst)

    def logUrlHeadersDataInst(self, url, headers, data, inst):
        self.log("request url: %s" % url)
        self.log("request headers: %s" % headers)
        self.log("request data: %s" % data)
        self.log("error: %s" % inst)

    def logLastStatusBodyHeadersMessageContentType(self):
        self.log('last status %s' % self.lastStatus)
        self.log('last body %s' % self.lastBody)
        self.log('last headers %s' % self.lastHeaders)
        self.log('last message %s' % self.lastMessage)
        self.log('last content type: %s' % self.lastContentType)

    def log(self, msg):
        if self.logger:
            logger.debug(msg)
        if self.isVerbose:
            print(msg)

    def jsonDumps(self, data):
        return json.dumps(data)
    
    def jsonLoads(self, string):
        try:
            if string == '':
                data = None
            else:
                data = json.loads(string)
        except ValueError, exception:
            msg = "Couldn't decode data from JSON string: '%s': %s" % (string, exception)
            raise ValueError, msg
        return data

