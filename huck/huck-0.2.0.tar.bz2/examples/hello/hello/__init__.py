from twisted import plugin
from twisted.application import service
from twisted.internet import reactor
from twisted.python import usage
from zope.interface import implements
from hello import handler
from hello import web

class Service(service.Service):

    def __init__(self, options):
        self.options = options
        self.factory = web.Application(handler.route, options)

    def startService(self):
        service.Service.startService(self)

        reactor.listenTCP(
            factory=self.factory,
            interface=self.options['interface'],
            port=self.options['port'],
        )

    def stopService(self):
        service.Service.stopService(self)

class Options(usage.Options):

    optParameters = [
        ['debug', '', True, None, bool],
        ['interface', 'i', 'localhost', None, unicode],
        ['port', 'p', 8000, None, int],
    ]

class ServiceMaker(object):
    implements(service.IServiceMaker, plugin.IPlugin)
    tapname = 'hello'
    description = 'A hello world application'
    options = Options

    def makeService(self, options):
        return Service(options)
