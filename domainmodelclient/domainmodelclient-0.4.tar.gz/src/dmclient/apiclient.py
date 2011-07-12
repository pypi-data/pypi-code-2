import os, urllib, urllib2, re

try: # Since Python 2.6.
    import json
except ImportError:
    import simplejson as json


class ApiError(Exception): pass

class ResourceError(ApiError): pass

class ContentTypeError(ApiError): pass


class ApiClient(object):

    apiKeyHeaderName = None
    resourcePaths = {}
    statusMessages = {
        200: 'OK',
        201: 'Created',
        301: 'Moved Permantently',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        409: 'Conflict',
        500: 'Service Error',
    }

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

    def getRegister(self, resourceName, *args):
        url = self.getUrl(resourceName, *args)
        return self.createResponse(url)

    def postRegister(self, data, resourceName, *args):
        url = self.getUrl(resourceName, *args)
        return self.createResponse(url, data)

    def getEntity(self, resourceName, *args):
        url = self.getUrl(resourceName, *args)
        return self.createResponse(url)

    def putEntity(self, data, resourceName, *args):
        url = self.getUrl(resourceName, *args)
        return self.createResponse(url, data)

    def getUrl(self, resourceName, *args):
        path = self.baseUrl
        path += self.resourcePaths[resourceName]
        path %= args
        return path

    def createResponse(self, url, data=None):
        self.data = data
        self.lastStatus = None
        self.lastBody = None
        self.lastHeaders = None
        self.lastMessage = None
        self.lastHttpError = None
        self.lastUrlError = None
        self.lastContentType = None
        self.lastCreatedLocation = None
        self.lastUrl = url
        self.log("Opening %s ..." % url)
        try:
            headers = {}
            if self.apiKey:
                headers[self.apiKeyHeaderName] = self.apiKey
            if self.data != None:
                data = self.jsonDumps(self.data)
                data = urllib.urlencode({data: 1})
            else:
                data = None
            httpRequest = urllib2.Request(url, data, headers)
            self.httpResponse = urllib2.urlopen(httpRequest)
        except urllib2.HTTPError, inst:
            self.logHttpError(url, headers, data, inst)
            self.lastHttpError = inst
            self.lastStatus = inst.code
            self.lastMessage = inst.read()
            self.raiseResourceError()
        except urllib2.URLError, inst:
            self.logUrlError(url, headers, data, inst)
            self.lastUrlError = inst
            self.lastStatus = inst.reason[0]
            self.lastMessage = inst.reason[1]
            self.raiseResourceError()
        else:
            self.log("OK opening resource at: %s" % url)

            self.lastStatus = self.httpResponse.code
            self.lastBody = self.httpResponse.read()
            self.lastHeaders = self.httpResponse.headers
            self.lastContentType = self.lastHeaders['Content-Type']
            if self.lastStatus == 201:
                self.lastCreatedLocation = self.lastHeaders['Location']
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

    def raiseResourceError(self):
        if self.lastStatus in self.statusMessages:
            statusMessage = "%s %s" % (self.lastStatus, self.statusMessages[self.lastStatus])
        else:
            statusMessage = "%s" % self.lastStatus
        msg = "Unable to open resource at %s: %s: %s" % (
            self.lastUrl, statusMessage, self.lastMessage)
        if self.data is not None:
            msg += ": %s" % self.data
        raise ResourceError(msg)

    def logHttpError(self, url, headers, data, inst):
        self.log("Received HTTP error code from Quant resource.")
        self.logUrlHeadersDataInst(url, headers, data, inst)

    def logUrlError(self, url, headers, data, inst):
        self.log("Unable to progress with URL.")
        self.logUrlHeadersDataInst(url, headers, data, inst)

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

