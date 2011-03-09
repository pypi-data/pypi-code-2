"""
StompProtocol
"""
try:
    import logging
    import pdb 
    import inject
    import stomper

    from twisted.internet.protocol import Protocol
    from twisted.internet import reactor
    from vmcontroller.common import support, exceptions
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

#@inject.appscope
class StompProtocol(Protocol):
    #transport available at self.transport, as set by BaseProtocol.makeConnection
    #factory available at self.factory, as set by Factory.buildProtocol

    stompEngine = inject.attr('stompEngine')
    config = inject.attr('config')

    def __init__(self):
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        self._username = self.config.get('broker', 'username')
        self._password = self.config.get('broker', 'password')

    def sendMsg(self, msg):
        self.logger.debug("Sending msg:\n %s" % msg)
        self.transport.write(msg)

    def connectionMade(self):
        """
        Called when a connection is made. 
        Protocol initialization happens here
        """
        self.logger.info("Connection with the broker made")
        stompConnectMsg = stomper.connect(self._username, self._password)
        self.sendMsg(stompConnectMsg)

        try:
            self.factory.resetDelay()
        except:
          pass

    def connectionLost(self, reason):
        """Called when the connection is shut down"""
        self.logger.info("Connection with the broker lost")

    def dataReceived(self, data):
        """Called whenever data is received"""
        reactions = self.stompEngine.react(data)
        if reactions:
            for reaction in filter(None,reactions):
                self.sendMsg(reaction)

