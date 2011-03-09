"""
StompProtocolFactory
"""
try:
    import logging
    import pdb 
    import inject
    import stomper

    from twisted.internet.protocol import ReconnectingClientFactory
    from twisted.internet import reactor
    from vmcontroller.common import support, exceptions
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

class StompProtocolFactory(ReconnectingClientFactory):
    """ Responsible for creating an instance of L{StompProtocol} """

    stompProtocol = inject.attr('stompProtocol')
    initialDelay = delay = 5.0
    factor = 1.0
    jitter = 0.0

    def __init__(self):
        #retry every 5 seconds, with no back-off
        self.protocol = lambda: self.stompProtocol #sigh... self.protocol must be callable
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))

    def clientConnectionLost(self, connector, reason):
        self.logger.info("Connection with the broker lost: %s" % reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.logger.error("Connection with the broker failed: %s" % reason )
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

