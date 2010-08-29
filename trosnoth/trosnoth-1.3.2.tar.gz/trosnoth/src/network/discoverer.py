# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''
trosnoth.src.network.discoverer
This module defines the network game discovery protocol. The protocol is used
to discover and broadcast information about Trosnoth games running on the
network and (if accessible) on the Internet.

Still to do:
Reduce amount of data when polling - keep track of those polling me
Interface to the rest of the game:
 - show message when games won't be visible on the Internet
 - game should tell discoverer if it can't connect to a server
'''

###########
# WARNING #
##############################################################################
# It is NOT A GOOD IDEA to modify the behaviour of this file too drastically #
# after the release of Trosnoth v1.1.0 because after this point there may be #
# games out there on the Internet which are using this protocol.             #
##############################################################################

import random
import socket

from twisted.internet import reactor, task, defer
from twisted.internet.error import CannotListenError
from twisted.internet.protocol import DatagramProtocol

from trosnoth.src.utils.utils import timeNow
from trosnoth.src.utils.unrepr import unrepr
from trosnoth.src.network.networkDefines import *
from trosnoth.src.network import netmsg
from trosnoth.src.network.discoverymsg import *

# knownServers is the collection of clients to connect to by default when
# asking about the existence of Internet games.
# Should be a collection of tuples of the form (ipAddress, port).
knownServers = (
    ('trosnoth.no-ip.org', 6700),  # avatar
    ('discoverer1.trosnoth.org', 6700),     # talljosh

    ('trosnoth.no-ip.org', 6789),  # avatar
    ('discoverer1.trosnoth.org', 6789),     # talljosh
)

def lanIP(addr):
    '''Returns True if the given IPv4 address is a LAN address,
    False otherwise.'''
    if addr.startswith('192.168.'):
        return True
    if addr.startswith('10.'):
        return True
    if addr.startswith('169.254.'):
        return True
    if addr == '127.0.0.1':
        return True
    if addr.startswith('172.') and addr[6] == '.':
        if 16 <= int(addr[4:6]) <= 31:
            return True
    return False

def log(message):
    if logMe:
        print 'Discoverer: %s' % (message,)

# verifyTime is the number of seconds to wait between verifying games.
# 1/4 of this time is used before the first verify.
verifyTime = 600
firstVerifyTime = verifyTime / 4.
verifyCheckTime = verifyTime / 20.

class DataValue(object):
    def __init__(self, value):
        self.value = value
        self.validateTime = timeNow() + firstVerifyTime

class DiscoveryHandler(object):
    '''
    A network message handler designed for use with trosnoth.network.netman.
    This is the main engine of the discovery protocol.
    '''
    greeting = 'GameDiscoveryProtocol1'
    messages = netmsg.MessageCollection(
        PeerRequestMsg,
        AcceptPeerMsg,
        DenyPeerMsg,
        LeavePeerMsg,

        QueryDataMsg,
        ResetDataMsg,
        UpdateDataMsg,
        DeleteDataMsg,
        QueryCompleteMsg,
        RefuseQueryMsg,

        VerifyDataMsg,
        ConfirmDataMsg,
        DenyDataMsg,

        DiagnosticRequestMsg,
        DiagnosticResponseMsg,
    )
    def __init__(self, netman, agent, defaultServers=knownServers,
            dataKind=''):
        '''
        If a dataKind is specified, only data of that kind will be remembered.
        '''
        self.idCode = ''.join(chr(random.randrange(256)) for i in xrange(8))
        self.netman = netman
        self.agent = agent
        self.dataKind = dataKind
        self.multicaster = UDPMulticaster(self._gotMulticastAnnounce)

        # data is a mapping from data kind to a mapping from (address, key)
        #   to DataValue.
        self.data = {}
        self.lanData = {}
        self.localData = {}
        self.recentIgnores = ExpiringDataStore()

        # peers is a list of peers on the Internet.
        # lanPeers is a list of peers on the LAN.
        self.peers = []
        self.lanPeers = []

        # lastPolled is the last server which was polled.
        self.lastPolled = None

        self.recentPollers = RecentPollers()

        # servers is a list of (ipAddress, port) combinations which have are
        #   Internet addresses and have not been discovered to be offline or
        #   unreachable.
        # lanServers is the same, but for LAN IP addresses.
        self.servers = []
        self.lanServers = []
        self.defaultServers = list(defaultServers)
        for address in defaultServers:
            self.tryAddress(address)

        # handlers is a mapping from connection id to the object which should
        #   handle that connection.
        self.handlers = {}

        # Connect to network manager.
        netman.addHandler(self)

        # Announce on multicast.
        self.multicaster.announce(netman.getTCPPort())

        # Start services which connect to new peers.
        self.peerConnector = PeerConnector(self)
        self.lanPeerConnector = PeerConnector(self, lan=True)
        self.serverPollDeferred = None
        self.serverPollKind = ''

        # Regurlarly validate data.
        self.dataValidator = DataValidator(self)

    def _dataValid(self):
        for db in self.data, self.localData, self.lanData:
            if not isinstance(db, dict):
                print 'Not dict'
                return False
            for kind,v in db.iteritems():
                if not isinstance(kind, str):
                    print 'kind not string: %r' % (kind,)
                    return False
                if not isinstance(v, dict):
                    print 'Map not dict: %r' % (v,)
                    return False
                for stdkey, value in v.iteritems():
                    if not isinstance(stdkey, tuple):
                        print 'stdkey not tuple: %r' % (stdkey,)
                        return False
                    if len(stdkey) != 2:
                        print 'len(stdkey) not 2: %r' % (stdkey,)
                        return False
                    address, key = stdkey
                    if not isinstance(key, str):
                        print 'key not string: %r' % (key,)
                        return False
                    if not isinstance(value, DataValue):
                        print 'value not DataValue: %r' % (value,)
                    if not isinstance(value.value, str):
                        print 'value.value not string: %r' % (value.value,)
        return True

    #############################
    # Interface to Trosnoth game
    #############################

    def kill(self):
        '''
        Stops any active behaviours of this object.
        '''
        self.peerConnector.kill()
        self.lanPeerConnector.kill()
        self.dataValidator.kill()

        # Disconnect from all peers.
        def disconnect(peers, lan):
            servers = []
            for server in peers:
                servers.append((server, self.get3Peers(lan, server)))
            for server, threePeers in servers:
                SendInfo(self, server, LeavePeerMsg(*threePeers))

        disconnect(self.peers, False)
        disconnect(self.lanPeers, True)

    def tryAddress(self, address):
        '''
        Adds the given address to the list of addresses to try.
        '''
        def gotHost(result):
            self.addServer((result, port))
            if result != host:
                log('resolved host %s to %s' % (host, result))
        def failure(reason):
            log('could not resolve %s: %s' % (host, reason))
        host, port = address
        reactor.resolve(host).addCallbacks(gotHost, failure)

    def loadPeers(self, f):
        '''
        Loads a list of peers from the given file.
        '''
        for line in f:
            address = unrepr(line)
            if not isinstance(address, tuple) or len(address) != 2:
                continue
            self.tryAddress(address)

    def savePeers(self, f):
        '''
        Saves a list of peers to the given file.
        '''
        for address in self.peers:
            f.write('%r\n' % (address,))
        for address in self.servers:
            f.write('%r\n' % (address,))

    def setData(self, kind, key, value, lanOnly=False):
        '''
        Sets the details of the currently running game. Should be called when
        a new server is started and when game details change.
        '''
        if kind == self.dataKind or self.dataKind == '':
            # Store the data.
            address = ('127.0.0.1', self.netman.getTCPPort())
            self._doDataSet(kind, address, key, DataValue(value))
        assert self._dataValid()

        # Send the info on.
        msg = UpdateDataMsg(address, kind, key, value)
        self.sendToPeers(msg, lanOnly)

    def delData(self, kind, key):
        '''
        Deletes some local data. Should be called when a game is
        over or no longer accepting connections.
        '''
        if kind == self.dataKind or self.dataKind == '':
            # Store the data.
            address = ('127.0.0.1', self.netman.getTCPPort())
            self._doDataRemove(kind, address, key, mustExist=False)
        assert self._dataValid()

        # Send the info on.
        msg = DeleteDataMsg(address, kind, key)
        self.sendToPeers(msg)

    def getData(self, kind=''):
        '''
        Returns a collection of all data which this client knows about which
        has the given data kind.

        Returns a deferred which results in a collection of tuples of the form
        ((ipAddr, port), kind, key, value).

        If the discoverer has been unable to connect as a peer to any Internet
        servers, it will poll one instead.
        '''
        if len(self.peers) == 0:
            # Not connected as peer to Internet.
            # Poll the Internet, but return current list.
            self.pollServer(kind)
            #return self.pollServer(kind)

        # Connected as peer, so just return the current list.
        result = self.getDataNow(kind)

        return defer.succeed(result)

    def cannotConnect(self, server):
        '''
        Tells the discovery server that the given server cannot be connected
        to.
        '''
        def removeFrom(lst):
            try:
                lst.remove(server)
            except ValueError:
                pass

        def removeGames(dta):
            # Remove any games on that server.
            for kind, data in dta.iteritems():
                for (svr, key) in data.keys():
                    if svr == server:
                        self._doDataRemove(kind, svr, key)

        if lanIP(server[0]):
            removeFrom(self.lanServers)
            removeFrom(self.lanPeers)
            removeGames(self.lanData)
        else:
            removeFrom(self.servers)
            removeFrom(self.peers)
            removeGames(self.data)
            if self.lastPolled == server:
                self.lastPolled = None
        assert self._dataValid()

    def isInternetAccessible(self):
        '''
        Returns a guess of whether this host is accessible from the Internet
        based on whether it has any Internet peers.
        '''
        return len(self.peers) != 0

    ###############################
    # Interface to network manager
    ###############################

    def newConnection(self, connId, ipAddr, port):
        '''
        Called by the network manager when an incoming connection is made.
        '''
        # Accept the connection, place a time-out and wait for it to say
        # what it wants.
        self.handlers[connId] = IncomingConnection(self, connId, ipAddr, port)

    def connectionComplete(self, connId):
        '''
        Called by the network manager when an outgoing connection is made.
        '''
        self.handlers[connId].connectionComplete(connId)

    def connectionLost(self, connId):
        '''
        Called by the network manager when a connection is lost.
        '''
        self.handlers[connId].connectionLost(connId)
        del self.handlers[connId]

    def connectionFailed(self, connId):
        '''
        Called by the network manager when an outgoing connection fails.
        '''
        self.handlers[connId].connectionFailed(connId)
        del self.handlers[connId]

    def receiveMessage(self, connId, msg):
        '''
        Called by the network manager when a message is received.
        '''
        self.handlers[connId].receiveMessage(connId, msg)

    ################
    # Other methods
    ################

    def getDataDict(self, server):
        if server == '127.0.0.1':
            return self.localData
        if lanIP(server):
            return self.lanData
        return self.data

    def _doDataRemove(self, kind, server, key, mustExist=True):
        data = self.getDataDict(server[0]).setdefault(kind, {})
        if mustExist or (server, key) in data:
            del data[server, key]
            self.recentPollers.dataRemoved(kind, server, key)

    def _doDataSet(self, kind, server, key, value):
        assert isinstance(value, DataValue)
        self.getDataDict(server[0]).setdefault(kind, {})[(server, key)] = value
        self.recentPollers.dataAdded(kind, server, key, value)

    def addServer(self, address):
        host, port = address
        if lanIP(host):
            if address in self.lanPeers:
                return
            if host != '127.0.0.1' or port != self.netman.getTCPPort():
                self.lanServers.append((host, port))
        else:
            if address in self.peers:
                return
            self.servers.append((host, port))

    def addPeer(self, address):
        host, port = address

        def addIt(servers, peers):
            for peer in list(peers):
                if peer[0] == address[0]:
                    if peer != address:
                        # Do not accept two peers at same IP address.
                        return False

                    # A peer's already connected and asks again. Allow.
                    peers.remove(address)
                    log('Peer confusion with: %s' % (address,))
            try:
                servers.remove(address)
            except ValueError:
                pass
            peers.append(address)
            if len(peers) == 1:
                # Poll the peer.
                log('len(peers) == 1')
                PollServer(self, self.dataKind, address)
            return True

        if lanIP(host):
            if addIt(self.lanServers, self.lanPeers):
                log('Added LAN peer: %s' % (address,))
        else:
            if addIt(self.servers, self.peers):
                log('Added Internet peer: %s' % (address,))

    def delPeer(self, ipAddr):
        def findAndDelete(peers, servers):
            for peer in peers:
                if peer[0] == ipAddr:
                    break
            else:
                return
            peers.remove(peer)
            servers.append(peer)

        if lanIP(ipAddr):
            findAndDelete(self.lanPeers, self.lanServers)
            log('Lost LAN peer: %s' % (ipAddr,))
        else:
            findAndDelete(self.peers, self.servers)
            log('Lost Internet peer: %s' % (ipAddr,))

    def delServer(self, server):
        try:
            if lanIP(server[0]):
                self.lanServers.remove(server)
            else:
                self.servers.remove(server)
        except ValueError:
            pass

    def isPeer(self, ipAddr):
        for peer in self.peers:
            if peer[0] == ipAddr:
                return True
        for peer in self.lanPeers:
            if peer[0] == ipAddr:
                return True
        return False

    def setHandler(self, connId, handler):
        self.handlers[connId] = handler

    def updateData(self, msg):
        '''Returns True if this is new information, False otherwise.'''
        if self.dataKind != msg.kind and self.dataKind != '':
            return self.recentIgnores.addData(msg.kind, msg.address,
                    msg.key, msg.value)

        if lanIP(msg.address[0]):
            data = self.lanData.setdefault(msg.kind, {})
        else:
            data = self.data.setdefault(msg.kind, {})
        stdkey = (msg.address, msg.key)

        # Check if we know this already.
        if stdkey in data and data[stdkey].value == msg.value:
            # We already know this.
            return False

        # Update the database.
        self._doDataSet(msg.kind, msg.address, msg.key, DataValue(msg.value))
        assert self._dataValid()
        return True

    def deleteData(self, msg):
        '''Returns True if this is new information, False otherwise.'''
        if self.dataKind != msg.kind and self.dataKind != '':
            return self.recentIgnores.delData(msg.kind, msg.address, msg.key)

        if lanIP(msg.address[0]):
            data = self.lanData.setdefault(msg.kind, {})
        else:
            data = self.data.setdefault(msg.kind, {})
        stdkey = (msg.address, msg.key)
        assert self._dataValid()

        # Check if we know this already.
        if stdkey not in data:
            # We already know this.
            return False

        # Update the database.
        self._doDataRemove(msg.kind, msg.address, msg.key)
        return True

    def resetData(self, kind, lan):
        if kind == '':
            if lan:
                self.lanData = {}
            self.data = {}
        else:
            if lan:
                self.lanData[kind] = {}
            self.data[kind] = {}
        assert self._dataValid()
        self.recentPollers.clear()

    def sendToPeers(self, msg, lanOnly=False, ignoreIPs=()):
        def sendIt(peers):
            for peer in peers:
                if peer[0] in ignoreIPs:
                    continue
                SendInfo(self, peer, msg)

        sendIt(self.lanPeers)
        if not lanOnly:
            sendIt(self.peers)

    def pollServer(self, kind):
        '''
        Polls an Internet server for games.
        '''
        # Check if we're already polling.
        if self.serverPollDeferred is not None:
            if kind == self.serverPollKind:
                log('Already polling, returning current poll.')
                return self.serverPollDeferred

            # Just return what we know already.
            result = defer.Deferred()
            result.callback(self.getDataNow(kind))
            log('Already polling with different kind.')
            return result

        # There's no current poll, so create one.
        self.serverPollDeferred = result = defer.Deferred()
        self.serverPollKind = kind
        def success(failure=None):
            self.serverPollDeferred = None
            data = self.getDataNow(kind)
            result.callback(data)
            return data

        PollAnyServer(self, kind).deferred.addCallbacks(success, success)
        return result

    def getDataNow(self, kind):
        result = []
        def addData1(data, kind, location):
            for (address, key), value in data.iteritems():
                result.append((address, kind, key, value.value, location))

        def addData(kind):
            # Add local, lan and Internet data.
            addData1(self.localData.setdefault(kind, {}), kind, 'local')
            addData1(self.lanData.setdefault(kind, {}), kind, 'lan')
            addData1(self.data.setdefault(kind, {}), kind, 'inet')

        if kind == '':
            allKinds = set(self.data.keys() + self.localData.keys()
                    + self.lanData.keys())
            for dKind in allKinds:
                addData(dKind)
        else:
            addData(kind)

        assert self._dataValid()
        return result

    def _gotMulticastAnnounce(self, server):
        '''
        A server announced itself on the multicast.
        '''
        # Remember that this server exists.
        self.addServer(server)

        # Attempt to connect to this server UNLESS we're in
        # the middle of a LAN peer attempt already.
        self.lanPeerConnector.makeAttempt(server)

    def get3Peers(self, lan, excludeIP=None):
        '''
        Gets and returns up to 3 peers of this discoverer.
        '''
        if lan:
            peers = list(self.lanPeers)
        else:
            peers = list(self.peers)

        if excludeIP in peers:
            peers.remove(excludeIP)

        result = []
        for i in xrange(3):
            if len(peers) == 0:
                result.append(('0.0.0.0', 0))
            else:
                i = random.randrange(len(peers))
                result.append(peers.pop(i))

        return result

    def rememberServers(self, msg, lan):
        # Remember the suggested servers.
        for addr, port in msg.server1, msg.server2, msg.server3:
            if addr == '0.0.0.0' or (lanIP(addr) != lan):
                continue
            self.addServer((addr, port))

class RecentPollers(object):
    '''
    Keeps track of clients who have recently polled this server.
    '''
    def __init__(self):
        self._pollData = {}
        self._pollTimes = {}

    def clear(self):
        self._pollData = {}
        self._pollTimes = {}

    def isPoller(self, ipAddr, port):
        return (ipAddr, port) in self._pollTimes

    def getPollData(self, ipAddr, port):
        if not self.isPoller(ipAddr, port):
            return None
        result = self._pollData[ipAddr, port]
        self.newPoller(ipAddr, port)
        return result

    def newPoller(self, ipAddr, port):
        self._pollData[ipAddr, port] = []
        self._pollTimes[ipAddr, port] = timeNow()
        self.purge()

    def purge(self):
        limit = timeNow() - 30
        for server, t in self._pollTimes.items():
            if t < limit:
                del self._pollTimes[server]
                del self._pollData[server]

    def getPollerCount(self):
        return len(self._pollData)

    def shouldAcceptPoll(self, ipAddr, port):
        if self.isPoller(ipAddr, port):
            return True
        excessPollers = self.getPollerCount() - 2
        if excessPollers <= 0:
            return True
        prob = 0.8 ** excessPollers
        return random.random() < prob

    def dataRemoved(self, kind, server, key):
        lanData = lanIP(server[0]) and server[0] != '127.0.0.1'
        msg = DeleteDataMsg(server, kind, key)
        for (host, port), data in self._pollData.iteritems():
            if lanIP(host) or not lanData:
                data.append(msg)

    def dataAdded(self, kind, server, key, value):
        lanData = lanIP(server[0]) and server[0] != '127.0.0.1'
        msg = UpdateDataMsg(server, kind, key, value.value)
        for (host, port), data in self._pollData.iteritems():
            if lanIP(host) or not lanData:
                data.append(msg)

class UDPMulticaster(object):
    def __init__(self, onAnnounce):
        # So that we can announce even if we can't listen.
        self.announcer = UDPMulticastAnnouncer()
        self.port = reactor.listenUDP(0, self.announcer)

        # Try multicast.
        self.listener = UDPMulticastListener(onAnnounce)
        self.tryListening()

    def tryListening(self):
        try:
            reactor.listenMulticast(multicastPort, self.listener)
        except CannotListenError:
            # Cannot listen to the multicast, possibly because another
            # instance is running on this computer.

            # Try listening again in 5 seconds.
            reactor.callLater(5, self.tryListening)

    def announce(self, tcpPort):
        try:
            self.announcer.announce(tcpPort)
        except socket.error, E:
            print 'Discoverer: could not announce on multicast: %s' % (E,)

class UDPMulticastListener(DatagramProtocol):
    def __init__(self, onAnnounce):
        self.onAnnounce = onAnnounce

    def startProtocol(self):
        # Join the correct multicast group.
        self.transport.joinGroup(multicastGroup)

    def datagramReceived(self, datagram, address):
        '''
        A multicast datagram has been received.
        '''
        # A server tells us that it exists
        if datagram.startswith('GameDiscoveryProtocol1:Hello:'):
            tcpPort = struct.unpack('!I', datagram[29:33])[0]
            self.onAnnounce((address[0], tcpPort))

class UDPMulticastAnnouncer(DatagramProtocol):
    def announce(self, tcpPort):
        # Tell the network that we exist.
        self.transport.write('GameDiscoveryProtocol1:Hello:' +
                struct.pack('!I', tcpPort), (multicastGroup, multicastPort))

class DataValidator(object):
    '''
    Regularly checks that data is still valid.
    '''
    def __init__(self, discoverer):
        self.discoverer = discoverer
        self._loop = task.LoopingCall(self._tick)
        self._loop.start(verifyCheckTime)

    def kill(self):
        if self._loop.running:
            self._loop.stop()

    def _tick(self):
        '''
        Called every so often to decide if anything needs to be done.
        '''

        t = timeNow()
        def validate(dataDict):
            for kind, data in dataDict.iteritems():
                for stdkey, dataVal in data.iteritems():
                    if t > dataVal.validateTime:
                        ValidateData(self.discoverer, data, kind, stdkey,
                                dataVal)

        validate(self.discoverer.data)
        validate(self.discoverer.lanData)

class PeerConnector(object):
    '''
    This object attempts to connect to peers in order to maintain a good
    number of peers for the discoverer.

    When first started, the PeerConnector will attempt to connect to peers at
    an interval of 1 second, but it will back off on failure until it is only 
    trying to connect every 10 minutes.

    The PeerConnector will attempt to connect to more peers or disconnect from
    peers in an attempt to keep the number of peers between 3 and 5.
    '''

    def __init__(self, discoverer, lan=False):
        self.discoverer = discoverer
        self.delay = 1
        self.attempt = None

        self.lan = lan
        if lan:
            self.peers = self.discoverer.lanPeers
            self.servers = self.discoverer.lanServers
        else:
            self.peers = self.discoverer.peers
            self.servers = self.discoverer.servers

        self._wait = None
        self._loop = task.LoopingCall(self._tick)
        self._loop.start(5)

    def kill(self):
        if self._loop.running:
            self._loop.stop()
        if self._wait is not None:
            self._wait.cancel()
            self._wait = None

    def _tick(self):
        '''
        Called every 5 seconds to decide if anything needs to be done.
        '''
        numPeers = len(self.peers)
        if numPeers < 3:
            if self.attempt is None and self._wait is None:
                self.delay = 1
                self.attemptConnecting()
        elif numPeers > 5:
            self.dropPeer()

    def attemptConnecting(self):
        if len(self.servers) == 0:
            # No servers are known to be up. Resort to default servers.
            for server in self.discoverer.defaultServers:
                if lanIP(server[0]) == self.lan:
                    self.discoverer.tryAddress(server)
            if len(self.servers) == 0:
                # No default servers.
                return

        # Select a server to connect to.
        server = self._server = random.choice(self.servers)

        # Attempt to connect to it.
        self.attempt = PeerAttempt(self, server)

    def makeAttempt(self, server):
        if self.attempt is None:
            self.attempt = PeerAttempt(self, server)

    def attemptSucceeded(self):
        log('Peer attempt succeeded')
        self.attempt = None

    def attemptFailed(self):
        self.attempt = None
        numPeers = len(self.peers)
        if numPeers < 3:
            if logMe:
                if self.lan:
                    lanText = 'a LAN'
                else:
                    lanText = 'an inet'
                log('Could not connect to %s peer. Waiting %s seconds.' %
                        (lanText, self.delay))
            self._wait = reactor.callLater(self.delay, self._waitComplete)

    def _waitComplete(self):
        self._wait = None
        numPeers = len(self.peers)
        if numPeers < 3 and self.attempt is None:
            self.delay = min(self.delay * 1.6, 1800)
            self.attemptConnecting()

    def dropPeer(self):
        '''
        Drops the oldest peer.
        '''
        if len(self.peers) == 0:
            return

        server = self.peers.pop(0)
        SendInfo(self.discoverer, server,
            LeavePeerMsg(*self.discoverer.get3Peers(self.lan)))

class PeerAttempt(object):
    greeting = DiscoveryHandler.greeting
    messages = DiscoveryHandler.messages

    def __init__(self, peerConnector, server):
        log('Attempting to connect to %s as peer' % (server,))
        self.peerConnector = peerConnector
        self.discoverer = peerConnector.discoverer
        self.netman = self.discoverer.netman
        self._timer = None

        ipAddr, port = self.server = server

        # Do not attempt to connect if the IP address is already a peer.
        for peer in self.peerConnector.peers:
            if peer[0] == ipAddr:
                self.failure()
                return

        self.connId = self.netman.connect(self, ipAddr, port)

        # NEXT: self.connectionComplete, self.connectionFailed

    def failure(self):
        '''
        Called when the attempt to connect to an Internet server as a peer
        failed.
        '''
        self.peerConnector.attemptFailed()

    def success(self):
        '''
        Called when the attempt to connect as a peer has succeeded.
        '''
        self.discoverer.addPeer(self.server)

        # Close the connection.
        self.netman.closeConnection(self.connId)
        self.connId = None

        # Inform PeerConnector.
        self.peerConnector.attemptSucceeded()

        # NEXT: connectionLost

    def connectionComplete(self, connId):
        '''
        Called by the network manager when an outgoing connection is made.
        '''
        assert connId == self.connId

        # Ask the remote end if we can be peers.
        self.netman.sendTCP(connId, PeerRequestMsg(
                self.netman.getTCPPort(),
                self.discoverer.idCode,
        ))

        # Set a time limit on the remote end responding.
        self._timer = reactor.callLater(5, self._timeout)

        # NEXT: self._timeout, self.connectionLost, self.receiveMessage

    def connectionFailed(self, connId):
        '''
        Called by the network manager when an outgoing connection fails.
        '''
        assert connId == self.connId

        # Could not connect to the given server, so remove it from the server
        # list.
        self.discoverer.cannotConnect(self.server)

        self.failure()

    def connectionLost(self, connId):
        '''
        Called by the network manager when a connection is lost.
        '''
        if self.connId is not None:
            if self._timer is not None:
                self._timer.cancel()
            self.failure()

    def receiveMessage(self, connId, msg):
        '''
        Called by the network manager when a message is received.
        '''
        assert connId == self.connId
        if isinstance(msg, AcceptPeerMsg):
            # Accepted as a peer of this host.
            if self._timer is not None:
                self._timer.cancel()
            self.success()
        elif isinstance(msg, DenyPeerMsg):
            # Denied as a peer of this host.
            if self._timer is not None:
                self._timer.cancel()

            # Remember the suggested peers.
            self.discoverer.rememberServers(msg, lanIP(self.server[0]))

            self.netman.closeConnection(self.connId)
            self.connId = None
            self.failure()

            # NEXT: connectionLost
        else:
            # Unexpected message: log it and ignore.
            print 'Discoverer: unexpected message: %s' % (type(msg),)

    def _timeout(self):
        '''
        Server took too long to accept the peer request.
        '''
        self.netman.closeConnection(self.connId)
        self.connId = None
        self.failure()

        # NEXT: connectionLost

class IncomingConnection(object):
    def __init__(self, discoverer, connId, ipAddr, port):
        self.discoverer = discoverer
        self.netman = discoverer.netman
        self.connId = connId
        self.ipAddr = ipAddr
        self.port = port

        # Set a time-out on this connection.
        self.timeout = reactor.callLater(10, self.timedOut)

    def timedOut(self):
        self.timeout = None
        self.netman.closeConnection(self.connId)

    def connectionLost(self, connId):
        '''
        Called by the network manager when a connection is lost.
        '''
        assert connId == self.connId
        if self.timeout is not None:
            self.timeout.cancel()
            self.timeout = None

    def receiveMessage(self, connId, msg):
        '''
        Called by the network manager when a message is received.
        '''
        assert connId == self.connId
        self.timeout.cancel()
        self.timeout = None

        kind = type(msg)
        if kind == PeerRequestMsg:
            if msg.idCode != self.discoverer.idCode:
                self.discoverer.setHandler(connId, 
                    PotentialPeer(self.discoverer, connId, self.ipAddr, msg))
                return
            # Remote end is self.
            log('%s identified as me' % (self.ipAddr,))
            server = (self.ipAddr, msg.port)
            if server in self.discoverer.defaultServers:
                self.discoverer.defaultServers.remove(server)
            self.discoverer.delServer(server)
        elif kind == LeavePeerMsg:
            self.discoverer.rememberServers(msg, lanIP(self.ipAddr))
            self.discoverer.delPeer(self.ipAddr)
        elif kind == QueryDataMsg:
            self.queryData(msg)
        elif kind == UpdateDataMsg:
            self.dataMsg(msg, self.discoverer.updateData)
        elif kind == DeleteDataMsg:
            self.dataMsg(msg, self.discoverer.deleteData)
        elif kind == VerifyDataMsg:
            self.verifyData(msg)
        elif kind == DiagnosticRequestMsg:
            self.diagnostics()
        else:
            print ('Discoverer: message not expected on new connection: %s'
                    % (kind,))
        self.netman.closeConnection(self.connId)

    def diagnostics(self):
        args = [self.discoverer.agent, len(self.discoverer.peers)]
        for i in xrange(min(5, len(self.discoverer.peers))):
            host, port = self.discoverer.peers[i]
            args.append((host, port))

        while len(args) < 7:
            args.append(('0.0.0.0', 0))

        msg = DiagnosticResponseMsg(*args)
        self.netman.sendTCP(self.connId, msg)

    def dataMsg(self, msg, recordData):
        if not self.discoverer.isPeer(self.ipAddr):
            # Not from a peer.
            return

        # Translate IP address.
        if msg.address[0] == '127.0.0.1':
            msg.address = (self.ipAddr, msg.address[1])
        else:
            # Check it's the correct zone.
            if lanIP(msg.address[0]):
                if not lanIP(self.ipAddr):
                    return

        if not recordData(msg):
            # Info is not new.
            return

        # Send info on to peers.
        self.discoverer.sendToPeers(msg, lanOnly=lanIP(self.ipAddr),
                ignoreIPs=(self.ipAddr, msg.address[0]))

    def queryData(self, msg):
        '''
        A QueryDataMsg has been received.
        '''
        log('Received poll from: %s' % (self.ipAddr,))

        recentPollers = self.discoverer.recentPollers

        if not recentPollers.shouldAcceptPoll(self.ipAddr, self.port):
            log('Denying poll')
            self.netman.sendTCP(self.connId, RefuseQueryMsg(
                    *self.discoverer.get3Peers(lanIP(self.ipAddr))))
            return

        pollData = recentPollers.getPollData(self.ipAddr, self.port)
        if pollData is not None:
            # We have stored poll data for this client.
            for msg in pollData:
                self.netman.sendTCP(self.connId, msg)
            self.netman.sendTCP(self.connId, QueryCompleteMsg())
            return

        # New poller.  Just clear the list and send the entire list.
        recentPollers.newPoller(self.ipAddr, self.port)
        self.netman.sendTCP(self.connId, ResetDataMsg())

        def sendSomeData(data, kind):
            for (addr, key), value in data.iteritems():
                msg = UpdateDataMsg(addr, kind, key, value.value)
                self.netman.sendTCP(self.connId, msg)

        def sendData(data):
            if msg.kind == '':
                for kind in data.keys():
                    sendSomeData(data[kind], kind)
            else:
                sendSomeData(data.get(msg.kind,{}), msg.kind)

        # Always send internet data.
        assert self.discoverer._dataValid()
        log('Replying to poll with internet and local data')
        sendData(self.discoverer.data)
        sendData(self.discoverer.localData)
        if lanIP(self.ipAddr):
            # To LAN hosts, send LAN data.
            log('Replying to poll with LAN data')
            sendData(self.discoverer.lanData)

        self.netman.sendTCP(self.connId, QueryCompleteMsg())

    def verifyData(self, msg):
        '''
        The behaviour in response to a verifyData request.
        '''
        log('Received verification request for %r / %r' % (msg.kind, msg.key))
        stdkey = (('127.0.0.1', self.netman.getTCPPort()), msg.key)
        try:
            dataVal = self.discoverer.localData.get(msg.kind,{})[stdkey]
        except KeyError:
            # Data not found.
            self.netman.sendTCP(self.connId, DenyDataMsg())
            log('Denying knowledge of data')
        else:
            # Data found. Return value.
            self.netman.sendTCP(self.connId, ConfirmDataMsg(dataVal.value))
            log('Confirming data')

        # Close the connection.
        self.netman.closeConnection(self.connId)

class PotentialPeer(object):
    greeting = DiscoveryHandler.greeting
    messages = DiscoveryHandler.messages

    def __init__(self, discoverer, connId, ipAddr, msg):
        self.discoverer = discoverer
        self.netman = discoverer.netman
        self.connId = connId
        self.lan = lanIP(ipAddr)

        if self.lan:
            peers = discoverer.peers
        else:
            peers = discoverer.lanPeers
        for peer in list(peers):
            if peer[0] == ipAddr:
                if peer[1] != msg.port:
                    # Don't accept the peer if we've already got a peer from
                    # that IP.
                    self.decline()
                    return
                # Already have this peer. Remove it and attempt re-add.
                discoverer.delPeer(ipAddr)

        # Attempt to connect to the peer.
        self.server = (ipAddr, msg.port)
        self.connId2 = self.netman.connect(self, ipAddr, msg.port)

    def connectionComplete(self, connId):
        assert connId == self.connId2
        netman = self.netman

        netman.closeConnection(self.connId2)
        if self.connId is None:
            # Remote end closed connection too early.
            return

        # Connected to peer, so accept the peer request.
        netman.sendTCP(self.connId, AcceptPeerMsg())
        self.discoverer.addPeer(self.server)

        # Close the connections.
        netman.closeConnection(self.connId)

    def connectionFailed(self, connId):
        assert connId == self.connId2

        # Could not connect to peer, so decline the peer request.
        self.decline()

        # Remember that we can't connect to this server.
        self.discoverer.cannotConnect(self.server)

    def decline(self):
        if self.connId is None:
            return

        self.netman.sendTCP(self.connId,
                DenyPeerMsg(*self.discoverer.get3Peers(self.lan)))
        self.netman.closeConnection(self.connId)

    def connectionLost(self, connId):
        # To be expected, so don't do anything.
        if connId == self.connId:
            self.connId = None

    def receiveMessage(self, connId, msg):
        # Should not receive a message on either connection.
        print 'Discoverer: PotentialPeer object received unexpected message'

class SendInfo(object):
    '''
    Opens a connection, sends the info, then closes the connection.
    '''
    greeting = DiscoveryHandler.greeting
    messages = DiscoveryHandler.messages

    def __init__(self, discoverer, address, msg):
        self.discoverer = discoverer
        self.netman = discoverer.netman
        self.address = address
        self.msg = msg
        self.connId = self.netman.connect(self, address[0], address[1])

    def connectionComplete(self, connId):
        assert connId == self.connId

        # Send the message then close the connection.
        self.netman.sendTCP(connId, self.msg)
        self.netman.closeConnection(connId)

    def connectionFailed(self, connId):
        assert connId == self.connId

        # Remember that we can't connect to this server.
        self.discoverer.cannotConnect(self.address)

    def connectionLost(self, connId):
        # To be expected.
        assert connId == self.connId

    def receiveMessage(self, connId, msg):
        # Should not receive a message on either connection.
        print 'Discoverer: SendInfo object received unexpected message'

class ExpiringDataStore(object):
    '''
    Used to store data that will expire. This is so that even what data being
    passed around is not data you're interested in, you don't pass on multiple
    messages about the same data event.
    '''

    def __init__(self):
        self.data = {}  # (kind, host, key) -> (value, callLater)

    def addData(self, kind, host, key, value):
        # Look up old entry.
        result = True
        if (kind, host, key) in self.data:
            oldValue, oldCallLater = self.data[kind, host, key]

            # Check if this is news.
            if oldValue == value:
                result = False

            # Cancel the old callLater.
            oldCallLater.cancel()

        # Create new entry.
        callLater = reactor.callLater(30, self._expired, (kind, host, key))
        self.data[kind, host, key] = (value, callLater)
        return result

    def delData(self, kind, host, key):
        return addData(kind, host, key, None)

class PollAnyServer(object):
    '''
    Polls an Internet server for games. Retries up to 3 times.
    '''
    def __init__(self, discoverer, kind):
        self.attempts = 0
        self.discoverer = discoverer
        self.kind = kind
        self.deferred = defer.Deferred()
        self.attemptPoll()

    def attemptPoll(self):
        self.attempts += 1

        # Select a server.
        server = self.discoverer.lastPolled
        if server is None:
            if len(self.discoverer.servers) == 0:
                self.deferred.errback(Exception('not connected to Internet'))
                return
            server = random.choice(self.discoverer.servers)

        self._lastServer = server
        PollServer(self.discoverer, self.kind, server).deferred.addCallbacks(
                self.deferred.callback, self.tryAgain)

    def tryAgain(self, failure):
        if self.attempts >= 3:
            log('Poll failed (%s)' % (self._lastServer,))
            self.deferred.errback(Exception('unable to poll Internet games'))
        else:
            log('Poll failed. Retrying. (%s)' % (self._lastServer,))
            self.attemptPoll()

class PollServer(object):
    '''
    Polls a given server for games.
    '''
    greeting = DiscoveryHandler.greeting
    messages = DiscoveryHandler.messages

    def __init__(self, discoverer, kind, server):
        self.discoverer = discoverer
        self.netman = discoverer.netman
        self.kind = kind
        self.ipAddr = server[0]
        self.server = server
        log('Polling server at %s' % (server,))
        discoverer.lastPolled = server
        self.connId = discoverer.netman.connect(self, server[0], server[1])

        self.deferred = defer.Deferred()

    def connectionComplete(self, connId):
        assert connId == self.connId

        # Send the query request.
        self.netman.sendTCP(connId, QueryDataMsg(self.kind))

    def connectionFailed(self, connId):
        assert connId == self.connId

        # Could not connect to the given server, so remove it from the server
        # list.
        self.discoverer.cannotConnect(self.server)
        self.deferred.errback(Exception('Cannot connect to server'))

    def connectionLost(self, connId):
        if self.connId is None:
            return

        # Query closed before completion.
        log('Remote discoverer did not complete the poll query response: %s'
                % (self.server,))
        self.deferred.errback(Exception(
                'Remote discoverer did not complete query response'))

    def receiveMessage(self, connId, msg):
        '''
        Called by the network manager when a message is received.
        '''
        assert connId == self.connId
        kind = type(msg)
        if kind is ResetDataMsg:
            self.discoverer.resetData(self.kind, lanIP(self.ipAddr))
        elif kind is UpdateDataMsg:
            self.dataMsg(msg, self.discoverer.updateData)
        elif kind is DeleteDataMsg:
            self.dataMsg(msg, self.discoverer.deleteData)
        elif kind is QueryCompleteMsg:
            self.netman.closeConnection(self.connId)
            self.connId = None
            self.deferred.callback(None)
        elif kind is RefuseQueryMsg:
            self.refusal(msg)
        else:
            print 'Discoverer: PollServer did not expect %s' % (kind,)
    
    def dataMsg(self, msg, recordData):
        # Translate IP address.
        if msg.address[0] == '127.0.0.1':
            msg.address = (self.ipAddr, msg.address[1])
        else:
            # Check it's the correct zone.
            if lanIP(msg.address[0]):
                if not lanIP(self.ipAddr):
                    return

        recordData(msg)

    def refusal(self, msg):
        '''
        A refusal was received.
        '''
        self.discoverer.rememberServers(msg, lanIP(self.ipAddr))
        self.netman.closeConnection(self.connId)
        self.connId = None
        self.deferred.errback(Exception('poll refused'))

class ValidateData(object):
    '''
    Validates a piece of data by checking with the server that hosts it.
    '''
    greeting = DiscoveryHandler.greeting
    messages = DiscoveryHandler.messages

    def __init__(self, discoverer, data, kind, stdkey, dataVal):
        self.discoverer = discoverer
        self.netman = discoverer.netman
        self.data = data
        self.kind = kind
        self.server, self.key = self.stdkey = stdkey
        self.dataVal = dataVal
        log('Validating data element %r with server at %s' % (self.key,
                self.server))
        self.connId = discoverer.netman.connect(self, *self.server)

        # Don't revalidate for a fixed length of time.
        dataVal.validateTime = timeNow() + verifyTime

    def connectionComplete(self, connId):
        assert connId == self.connId

        # Send the query request.
        self.netman.sendTCP(connId, VerifyDataMsg(self.kind, self.key))

    def connectionFailed(self, connId):
        assert connId == self.connId

        # Could not connect to the given server, so remove it from the server
        # list.
        self.discoverer.cannotConnect(self.server)
        self.failed()

    def failed(self):
        # Delete the data.
        del self.data[self.stdkey]
        log('Validation failed: %r' % (self.stdkey,))

    def connectionLost(self, connId):
        if self.connId is None:
            return

        self.failed()

    def receiveMessage(self, connId, msg):
        '''
        Called by the network manager when a message is received.
        '''
        assert connId == self.connId
        kind = type(msg)
        if kind is ConfirmDataMsg:
            self.dataVal.value = msg.value
            log('Validation successful: %r' % (self.stdkey,))
        elif kind is DenyDataMsg:
            self.failed()
        else:
            print 'Discoverer: VerifyData did not expect %s' % (kind,)

        self.netman.closeConnection(connId)
        self.connId = None

def main(enableLogging=True):
    from trosnoth.src.network.netman import NetworkManager

    global logMe
    logMe = enableLogging

    # If there's an argument, use it.
    import sys
    if len(sys.argv) == 1:
        tPort = 6700
        uPort = 6700
    elif len(sys.argv) == 2:
        tPort = uPort = int(sys.argv[1])
    elif len(sys.argv) == 3:
        tPort = int(sys.argv[1])
        uPort = int(sys.argv[2])
    else:
        print 'Usage:'
        print '  %s [tcp_port [udp_port]]' % (sys.argv[0],)
        return

    # Start the discoverer.
    print 'Starting game discovery service...'
    netman = NetworkManager(tPort, uPort)
    handler = DiscoveryHandler(netman, 'discovery-server-0.0.1')

    reactor.run()

if __name__ == '__main__':
    logMe = True
    main()
else:
    logMe = False
