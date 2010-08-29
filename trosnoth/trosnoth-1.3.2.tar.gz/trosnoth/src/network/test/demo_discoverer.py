
import random

from twisted.internet import task, reactor
from trosnoth.src.network.discoverer import *
from trosnoth.src.network.netman import NetworkManager

# Optional: make handler 3 unreachable.
if False:
    class MyNetworkManager(NetworkManager):
        def connect(self, handler, ipAddress, port, timeout=7):
            if port == netman3.getTCPPort():
                reactor.callLater(0, self._failMiserably, handler)
                return -1
            else:
                return NetworkManager.connect(self, handler, ipAddress, port,
                        timeout)

        def _failMiserably(self, handler):
            handler.connectionFailed(-1)
else:
    MyNetworkManager = NetworkManager

# Construct one upstream network manager and handler and two downstream.
# Optional: comment out "netman =" and "handler =" for no upstream handler.
netman = MyNetworkManager(6700, 6700)
netman2 = MyNetworkManager(0, 0)
netman3 = MyNetworkManager(0, 0)

handler = DiscoveryHandler(netman, 'test_discoverer', ())
handler2 = DiscoveryHandler(netman2, 'test_discoverer', [('127.0.0.1', 6700)])
handler3 = DiscoveryHandler(netman3, 'test_discoverer', [('127.0.0.1', 6700)])

# Every 1 second, handler 3 will tell us what games it knows about.
def reportGames():
    print handler3.getData()
    for k,v in handler3.conns.iteritems():
        print '  %s: %s' % (k, v)
task.LoopingCall(reportGames).start(1)

# Every 10 seconds, handler 2 may add or remove a game.
def doSomething(count=[0]):
    val = random.random()
    if val < 0.5:
        # Add a game.
        i = count[0]
        print 'Adding game %d **********************' % (i,)
        handler2.setData('TestGame', str(i), 'Settings'+str(i))
        print 'Game %d added ***********************' % (i,)
        count[0] += 1
    elif val < 0.9:
        # Remove a game.
        if count[0] > 0:
            i = count[0] - 1
            print 'Removing game %d ***********************' % (i,)
            handler2.delData('TestGame', str(i))
            print 'Game %d removed ************************' % (i,)
            count[0] -= 1
task.LoopingCall(doSomething).start(10)

reactor.run()
