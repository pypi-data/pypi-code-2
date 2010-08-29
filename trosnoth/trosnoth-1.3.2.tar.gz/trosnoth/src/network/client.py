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

from trosnoth.src.network import netmsg
from trosnoth.src.network.networkDefines import validServerVersions
from trosnoth.src.messages import (ChatMsg, TaggingZoneMsg, NotifyUDPStatusMsg,
        RequestUDPStatusMsg, PlayerStarsSpentMsg, PlayerHasUpgradeMsg,
        DeleteUpgradeMsg, CannotBuyUpgradeMsg, GameStartMsg, GameOverMsg,
        StartingSoonMsg, SetTeamNameMsg, SetGameModeMsg, ShotFiredMsg,
        KillShotMsg, RespawnMsg, PlayerKilledMsg, PlayerUpdateMsg,
        CannotRespawnMsg, AddPlayerMsg, JoinSuccessfulMsg, UpdatePlayerStateMsg,
        AimPlayerAtMsg, RemovePlayerMsg, CannotJoinMsg, SetCaptainMsg,
        TeamIsReadyMsg, InitClientMsg, ConnectionLostMsg,
        SetWorldParametersMsg, MapBlockLayoutMsg, ZoneStateMsg, tcpMessages)
from trosnoth.src.utils.components import Component, Plug
from trosnoth.src.utils.unrepr import unrepr
from twisted.internet import defer, reactor

clientMsgs = netmsg.MessageCollection(
    NotifyUDPStatusMsg,
    InitClientMsg,
    SetWorldParametersMsg,
    MapBlockLayoutMsg,
    CannotJoinMsg,
    DeleteUpgradeMsg,
    GameStartMsg,
    TaggingZoneMsg,
    PlayerStarsSpentMsg,
    PlayerHasUpgradeMsg,
    KillShotMsg,
    ShotFiredMsg,
    AddPlayerMsg,
    RespawnMsg,
    UpdatePlayerStateMsg,
    AimPlayerAtMsg,
    PlayerKilledMsg,
    GameOverMsg,
    SetCaptainMsg,
    TeamIsReadyMsg,
    StartingSoonMsg,
    SetTeamNameMsg,
    SetGameModeMsg,
    JoinSuccessfulMsg,
    RemovePlayerMsg,
    PlayerUpdateMsg,
    CannotRespawnMsg,
    CannotBuyUpgradeMsg,
    ChatMsg,
    ZoneStateMsg,
)

class ConnectionFailed(Exception):
    def __init__(self, reason):
        self.reason = reason

class ClientNetHandler(Component):
    requestPlug = Plug()
    eventPlug = Plug()

    greeting = 'Trosnoth1'
    messages = clientMsgs

    def __init__(self, netman):
        Component.__init__(self)
        self.netman = netman
        self.connId = None
        self.validated = False
        self._deferred = None
        self.udpWorks = True

    def newConnection(self, connId, ipAddr, port):
        'Should never happen.'

    def makeConnection(self, host, port, timeout=7):
        assert self._deferred is None, 'Already connecting.'
        self.connId = None
        self.validated = False
        self._deferred = result = defer.Deferred()
        self.netman.connect(self, host, port, timeout)
        reactor.callLater(timeout, self._timedOut)
        return result

    def _timedOut(self):
        if self.connId is None or not self.validated:
            if self._deferred is not None:
                self._deferred.errback(ConnectionFailed('Timed out.'))
                self._deferred = None

    def cancelConnecting(self):
        if self.connId is not None:
            self.netman.closeConnection(self.connId)
            self.connId = None

    def disconnect(self):
        if self.connId is not None:
            self.netman.closeConnection(self.connId)
            self.connId = None

    def connectionComplete(self, connId):
        self.connId = connId

    def receiveMessage(self, connId, msg):
        if self._deferred is not None:
            if isinstance(msg, InitClientMsg):
                self._receiveInitClientMsg(msg)
        elif isinstance(msg, NotifyUDPStatusMsg):
            self._receiveNotifyUDPStatusMsg(msg)
        else:
            self.eventPlug.send(msg)

    def _receiveInitClientMsg(self, msg):
        # Settings from the server.
        settings = unrepr(msg.settings)

        # Check that we recognise the server version.
        svrVersion = settings.get('serverVersion', 'server.v1.0.0+')
        if svrVersion not in validServerVersions:
            print 'Client: bad server version %s' % (svrVersion,)
            self._deferred.errback(ConnectionFailed('Incompatible server version.'))
            self._deferred = None
            self.netman.closeConnection(self.connId)
            self.connId = None
            return

        # Tell the client that the connection has been made.
        self.validated = True
        self._deferred.callback(settings)
        self._deferred = None

        # Wait 10 seconds then check if UDP is working.
        reactor.callLater(10, self._checkUDP)

    def _checkUDP(self):
        '''
        Sends a message to the server asking whether UDP works or not.
        To prevent this message from flying around out of control, this method
        should only be called once after the connection is validated, and then
        from the receiveNotifyUDPStatusMsg method as need be.
        '''
        if self.connId is not None:
            self.netman.sendTCP(self.connId, RequestUDPStatusMsg())

    def _receiveNotifyUDPStatusMsg(self, msg):
        '''
        The server is sending notification as to whether or not UDP messages
        from the server can get through to the client.
        '''
        udpWorks = bool(msg.connected)
        if not udpWorks:
            # Check again in 10 seconds.
            reactor.callLater(10, self._checkUDP)

        # Notify the client.
        if udpWorks != self.udpWorks:
            self.eventPlug.send(msg)

        self.udpWorks = udpWorks

    @requestPlug.defaultHandler
    def requestMsg(self, msg):
        # TODO: Ascertain whether to use TCP based on whether message is in
        # a particular set of message types.
        if self.connId is not None:
            if msg.__class__ in tcpMessages:
                self.netman.sendTCP(self.connId, msg)
            else:
                self.netman.send(self.connId, msg)

    def receiveBadString(self, connId, line):
        if self._deferred is not None:
            self._deferred.errback(ConnectionFailed('Remote host sent unexpected '
                    'message: %r' % (line,)))
            self._deferred = None
            self.connId = None
            self.netman.closeConnection(connId)
            return
        print 'Client: Unknown message: %r' % (line,)
        print '      : Did you invent a new network message and forget to'
        print '      : add it to trosnoth.network.client.clientMsgs?'

    def connectionLost(self, connId):
        self.connId = None
        if self._deferred is not None:
            self._deferred.errback(
                    ConnectionFailed('Remote server dropped connection.'))
            self._deferred = None
            return
        self.eventPlug.send(ConnectionLostMsg())

    def connectionFailed(self, connId):
        if self._deferred is not None:
            self._deferred.errback(ConnectionFailed('Timed out.'))
            self._deferred = None
            self.connId = None

