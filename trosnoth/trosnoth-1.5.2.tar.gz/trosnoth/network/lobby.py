# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
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

import logging
import pickle
import socket

from trosnoth import rsa
from trosnoth.network import authcommands
from trosnoth.network.client import ClientNetHandler
from trosnoth.network.networkDefines import (validServerVersions, serverVersion,
        multicastPort, multicastGroup)
from trosnoth.utils.unrepr import unrepr
from twisted.internet.error import CannotListenError
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator, DatagramProtocol
from twisted.protocols import amp
from trosnoth.utils.twist import WeakCallLater

log = logging.getLogger('lobby')

class PasswordGetter(object):
    '''
    Interface for password getters, which must be used as a parameter to
    lobby.Game.join() below.
    '''
    def getPassword(self, host, errorText=''):
        '''
        Returns a deferred whose callback will be executed with (create,
        username, password), where create is a boolean indicating whether the
        account should be created. If the user cancels the getPassword(), the
        deferred's callback will be executed with an argument of None.

        @errorText: Should be provided if the previous password was invalid or
                the host refused to create a user.
        '''

class Game(object):
    '''
    Interface for lobby.Game objects.
    '''
    def join(self, passwordGetter):
        '''
        Connects to the game and returns a deferred whose callback will be
        executed with (netHandler, authTag).
        @param passwordGetter: an object satisfying the PasswordGetter
            interface, used if authentication is needed to join this game.
        '''

class AuthenticationCancelled(Exception):
    '''
    Raised in Game.join() if authentication was required and the user cancelled
    the password dialogue box.
    '''

class AuthGame(Game):
    def __init__(self, lobby, server, id):
        self.lobby = lobby
        self.server = server
        self.id = id

    @defer.deferredGenerator
    def join(self, passwordGetter):
        '''
        Attempts to connect to this game. Returns a deferred whose
        callback will be executed with (netHandler, authTag).
        '''
        host, port = self.server
        p = defer.waitForDeferred(ClientCreator(reactor,
                amp.AMP).connectTCP(host, port))
        yield p
        p = p.getResult()

        try:
            result = defer.waitForDeferred(p.callRemote(
                    authcommands.ConnectToGame, id=self.id))
            yield result
            result = result.getResult()
        except authcommands.NotAuthenticated:
            a = defer.waitForDeferred(self.lobby._authenticate(p, host,
                    passwordGetter))
            yield a
            a.getResult()

            result = defer.waitForDeferred(p.callRemote(
                    authcommands.ConnectToGame, id=self.id))
            yield result
            result = result.getResult()

        netHandler = defer.waitForDeferred(self.lobby._connectToServer(host,
                result['port']))
        yield netHandler
        netHandler = netHandler.getResult()
        self.lobby.app.identitySettings.setNick(result['nick'])
        yield (netHandler, result['authTag'])


class NonAuthGame(Game):
    def __init__(self, lobby, ipAddr, port):
        self.lobby = lobby
        self.ip = ipAddr
        self.port = port

    @defer.deferredGenerator
    def join(self, passwordGetter):
        '''
        Attempts to connect to the given lobby.Game. Returns a deferred whose
        callback will be executed with (netHandler, authTag).
        '''
        netHandler = defer.waitForDeferred(self.lobby._connectToServer(self.ip,
                self.port))
        yield netHandler
        netHandler = netHandler.getResult()
        yield (netHandler, 0)

class IncorrectServerVersion(Exception):
    '''
    The server created a game of the wrong version.
    '''

class Lobby(object):
    '''
    Performs tasks related to finding games and joining them.
    '''
    def __init__(self, app, netman):
        self.app = app
        self.netman = netman

    @defer.deferredGenerator
    def getGames(self, server, timeout=2):
        '''
        Connects to an authentication server and asks it for the available
        games on that server. Returns a deferred whose callback will be executed
        with a list of lobby.Game objects.
        @param server: A tuple of (host, port).
        '''
        host, port = server
        p = defer.waitForDeferred(ClientCreator(reactor,
                amp.AMP).connectTCP(host, port, timeout=timeout))
        yield p
        p = p.getResult()
        result = defer.waitForDeferred(p.callRemote(authcommands.ListGames))
        yield result
        result = result.getResult()
        games = []
        for item in result['games']:
            if (item['game'] == 'Trosnoth1' and item['version'] in
                    validServerVersions):
                games.append(AuthGame(self, server, item['id']))

        yield games

    @defer.deferredGenerator
    def getOtherGames(self, server, timeout=2):
        '''
        Connects to an authentication server and asks it for the available
        games it knows about which are not hosted on that server. Returns a
        deferred whose callback will be executed with a list of lobby.Game
        objects.
        @param server: A tuple of (host, port).
        '''
        host, port = server
        p = defer.waitForDeferred(ClientCreator(reactor,
                amp.AMP).connectTCP(host, port, timeout=timeout))
        yield p
        p = p.getResult()
        result = defer.waitForDeferred(p.callRemote(
                authcommands.ListOtherGames))
        yield result
        result = result.getResult()
        games = []
        for item in result['games']:
            if (item['game'] == 'Trosnoth1' and item['version'] in
                    validServerVersions):
                games.append(NonAuthGame(self, item['ip'], item['port']))

        yield games

    @defer.deferredGenerator
    def getMulticastGames(self):
        '''
        Returns a deferred which will be called back with a sequence of Game
        objects representing the games which could be found on the LAN by
        multicasting a game request.
        '''
        games = defer.waitForDeferred(getMulticastGames())
        yield games
        games = games.getResult()

        result = []
        for (ip, port), gameInfo in games:
            result.append(NonAuthGame(self, ip, port))
        yield result

    @defer.deferredGenerator
    def registerGame(self, server, netHandler, timeout=2):
        '''
        Registers the game running on the given ServerNetHandler with the given
        authentication server. Returns a deferred whose callback will be
        executed with True or False indicating whether the registration has been
        successful.
        @param server: A tuple of (host, port).
        '''
        host, port = server

        p = defer.waitForDeferred(ClientCreator(reactor,
                amp.AMP).connectTCP(host, port, timeout=timeout))
        yield p
        p = p.getResult()
        result = defer.waitForDeferred(p.callRemote(authcommands.RegisterGame,
                game='Trosnoth1', version=serverVersion,
                port=netHandler.netman.getTCPPort()))
        yield result
        try:
            result = result.getResult()
        except:
            yield False

        yield True

    @defer.deferredGenerator
    def startGame(self, server, passwordGetter):
        '''
        Attempts to start a game on the given server, and connects to the
        newly-created game. Returns a deferred whose callback will be executed
        with (netHandler, authTag).
        @param server: A tuple of (host, port).
        @param passwordGetter: PasswordGetter object which is used to
            authenticate with the server if needed.
        '''
        host, port = server
        p = defer.waitForDeferred(ClientCreator(reactor,
                amp.AMP).connectTCP(host, port))
        yield p
        p = p.getResult()

        result = defer.waitForDeferred(p.callRemote(authcommands.CreateGame,
                game='Trosnoth1'))
        yield result
        result = result.getResult()
        if result['version'] not in validServerVersions:
            raise IncorrectServerVersion()

        game = AuthGame(self, server, result['id'])

        result = defer.waitForDeferred(game.join(passwordGetter))
        yield result
        yield result.getResult()

    @defer.deferredGenerator
    def _connectToServer(self, host, port):
        netHandler = ClientNetHandler(self.netman)
        result = defer.waitForDeferred(netHandler.makeConnection(host, port))
        yield result
        result.getResult()

        yield netHandler

    @defer.deferredGenerator
    def _authenticate(self, p, host, passwordGetter):
        errorMsg = ''
        while True:
            if host in AUTHENTICATION_CACHE:
                create = False
                username, password = AUTHENTICATION_CACHE[host]
            else:
                result = defer.waitForDeferred(passwordGetter.getPassword(host,
                        errorMsg))
                yield result
                result = result.getResult()
                if result is None:
                    raise AuthenticationCancelled()
                create, username, password = result

            token = defer.waitForDeferred(p.callRemote(
                    authcommands.GetAuthToken))
            yield token
            token = token.getResult()['token']

            pubkey = defer.waitForDeferred(p.callRemote(
                    authcommands.GetPublicKey))
            yield pubkey
            pubkey = makePublicKey(pubkey.getResult())

            data = rsa.encrypt(token + password.encode(), pubkey)

            if create:
                result = defer.waitForDeferred(p.callRemote(
                        authcommands.CreateUserWithPassword,
                        username=str(username), password=data))
                yield result
                result = result.getResult()['result']
                if result == '':
                    return  # Authentication successful.
                errorMsg = result
            else:
                result = defer.waitForDeferred(p.callRemote(
                        authcommands.PasswordAuthenticate,
                        username=str(username), password=data))
                yield result
                result = result.getResult()['result']
                if result:
                    return  # Authentication successful.
                errorMsg = 'Bad username/password'

AUTHENTICATION_CACHE = {}   # host -> (username, password)

def makePublicKey(result):
    '''
    Takes the result of the GetPublicKey amp call and converts it into a public
    key which the rsa module can handle.
    '''
    return result
    return {
        'e': pickle.decode_long(result['e']),
        'n': pickle.decode_long(result['n']),
    }

class UDPMulticaster(object):
    def __init__(self, gameGetter):
        self.stopped = False
        self.port = None
        self.listener = UDPMulticastListener(gameGetter)
        self.tryListening()

    def stop(self):
        if self.port is not None:
            self.port.stopListening()
        self.stopped = True

    def tryListening(self):
        if self.stopped:
            return
        try:
            self.port = reactor.listenMulticast(multicastPort, self.listener)
        except CannotListenError:
            # Cannot listen to the multicast, possibly because another
            # instance is running on this computer.

            # Try listening again in 5 seconds.
            WeakCallLater(5, self, 'tryListening')

MULTICAST_PROTOCOL_NAME = 'TrosnothMulticastProtocol1'

class UDPMulticastListener(DatagramProtocol):
    def __init__(self, gameGetter):
        '''
        gameGetter must be callable, and return a sequence of game information
        dicts, each of which must contain:
            ['port'] - the port this game is listening on
            ['version'] - the version string
            ['name'] - the game name
        '''
        self.getGames = gameGetter

    def startProtocol(self):
        # Join the correct multicast group.
        self.transport.joinGroup(multicastGroup)

    def datagramReceived(self, datagram, address):
        '''
        A multicast datagram has been received.
        '''
        if datagram == '%s:GetGames' % (MULTICAST_PROTOCOL_NAME,):
            for game in self.getGames():
                self.transport.write('%s:Game:%s' % (MULTICAST_PROTOCOL_NAME,
                        repr(game),), address)

class UDPMulticastGameGetter(DatagramProtocol):
    def __init__(self):
        self.port = reactor.listenUDP(0, self)
        self._deferred = None
        self._games = []

    def stop(self):
        self.port.stopListening()

    def getGames(self, timeout=1):
        '''
        Returns a deferred which will be called back with a sequence of
        (address, info) where info is a dict which has:
            ['name'] - the name of the game
            ['version'] - the version string of the game
        '''
        d= defer.Deferred()
        try:
            self.transport.write('%s:GetGames' % MULTICAST_PROTOCOL_NAME,
                    (multicastGroup, multicastPort))
        except socket.error, e:
            log.info('Could not request games from multicast: %s', e)
            d.callback([])
            return d

        self._deferred = d
        self._games = []

        WeakCallLater(timeout, self, '_gotGames', d)

        return d

    def _gotGames(self, d):
        d.callback(self._games)
        self._deferred = None
        self._games = []

    def datagramReceived(self, datagram, address):
        '''
        A reply to our query has been received.
        '''
        if self._deferred is None:
            return
        if datagram.startswith('%s:Game:' % (MULTICAST_PROTOCOL_NAME,)):
            gameInfo = unrepr(datagram[len('%s:Game:' %
                    (MULTICAST_PROTOCOL_NAME,)):])
            gameAddress = (address[0], gameInfo.pop('port'))
            self._games.append((gameAddress, gameInfo))

def getMulticastGames(timeout=1):
    getter = UDPMulticastGameGetter()
    d = getter.getGames(timeout)
    @d.addCallback
    def gotGames(games):
        getter.stop()
        return games
    return d
