"""This code is adapted from twisted.web.client to provide a getPage
function whose callback is called with a tuple containing the status, the
response headers, and the payload.  We need to look in the headers to get
content type when doing a GET on a tag value in order to create a Blob
result.

We also treat 204 (No Content) status results as not being errors, as
FluidDB returns a 204 in various cases."""

from twisted.internet import reactor
from twisted.web import client, error



class HTTPError(error.Error):
    def __init__(self, code, message=None, response=None,
                 response_headers=None):
        error.Error.__init__(self, code, message, response)
        self.response_headers = response_headers



class HTTPPageGetter(client.HTTPPageGetter):
    handleStatus_204 = lambda self: self.handleStatus_200()



class HTTPClientFactory(client.HTTPClientFactory):
    protocol = HTTPPageGetter

        
    def page(self, page):
        if self.waiting:
            self.waiting = 0
            self.deferred.callback((self.status, self.response_headers, page))


    def noPage(self, reason):
        if self.waiting:
            self.waiting = 0
            value = reason.value
            if isinstance(value, error.Error):
                reason = HTTPError(value.status, value.message,
                                   value.response, self.response_headers)
            self.deferred.errback(reason)


def getPage(url, contextFactory=None, *args, **kwargs):
    scheme, host, port, path = client._parse(url)
    factory = HTTPClientFactory(url, *args, **kwargs)
    if scheme == 'https':
        from twisted.internet import ssl
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    
    return factory.deferred
