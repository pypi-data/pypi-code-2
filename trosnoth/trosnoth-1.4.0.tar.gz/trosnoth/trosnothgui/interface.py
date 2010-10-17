# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2010 Joshua D Bartlett
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

'''interface.py - defines the Interface class which deals with drawing the
game to the screen, including menus and other doodads.'''

import pygame

from trosnoth.network.client import ClientNetHandler, ConnectionFailed
from trosnoth.game import makeIsolatedGame
from trosnoth.gamerecording import replays

from trosnoth.gui.framework import framework, elements

from trosnoth.trosnothgui.pregame.startupInterface import StartupInterface
from trosnoth.trosnothgui.pregame.connectingScreen import ConnectingScreen
from trosnoth.trosnothgui.pregame.backdrop import TrosnothBackdrop

from trosnoth.trosnothgui.pregame.connectionFailedDialog import ConnectionFailedDialog
from trosnoth.trosnothgui.ingame.gameInterface import GameInterface

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)

        # Create an interfaces for pre- and post-connection.
        self.backdrop = TrosnothBackdrop(app)
        self.startupInterface = StartupInterface(app, self)

        self._buildPointer()
        self.gi = None
        self.game = None
        self.netHandler = None
        self.agentId = None

        self.elements = [self.backdrop, self.startupInterface]

    def _buildPointer(self):
        img = self.app.theme.sprites.pointer
        pointer = elements.PictureElement(self.app, img, pygame.mouse.get_pos())
        self.app.screenManager.setPointer(pointer)
        pygame.mouse.set_visible(0)

    def processEvent(self, event):
        # Capture the quit event.
        if event.type == pygame.QUIT:
            self.app.stop()
            return
        return super(Interface, self).processEvent(event)

    def connectToServer(self, host, port):
        self.elements = [
            self.backdrop,
            ConnectingScreen(self.app, '%s:%s' % (host, port),
                onCancel=self.cancelConnecting)
        ]

        self.netHandler = ClientNetHandler(self.app.netman)
        result = self.netHandler.makeConnection(host, port)
        result.addCallback(lambda r: self.connectionEstablished()).addErrback(
                self.connectionFailed)
        return result

    def cancelConnecting(self, source):
        self.startupInterface.mainMenu()
        self.netHandler.cancelConnecting()
        self.netHandler = None

    def connectedToGame(self, netHandler, authTag):
        self.netHandler = netHandler
        self.connectionEstablished(authTag)

    def connectToLocalServer(self):
        '''
        Requries app.server is not None. Connects to the locally-hosted server.
        '''
        self.startupInterface.mainMenu()

        self.game = game = self.app.server.game
        self.setupGame(game, 0)

        self.elements = [self.gi]

    def connectionEstablished(self, authTag=0):
        'Called when this client establishes a connection to a server.'
        self.startupInterface.mainMenu()

        game, eventPlug, controlPlug = makeIsolatedGame(
                self.app.layoutDatabase)
        self.netHandler.requestPlug.connectPlug(controlPlug)
        self.netHandler.eventPlug.connectPlug(eventPlug)

        self.setupGame(game, authTag)
        game.syncWorld()

        self.game = game
        self.elements = [self.gi]

    def setupGame(self, game, authTag):
        # Create a game interface.
        self.gi = gi = GameInterface(self.app, game.world,
                onDisconnectRequest=self._disconnectGame,
                onConnectionLost=self.connectionLost, authTag=authTag)
        self.agentId = game.addAgent(gi.eventPlug, gi.controller)

    def setupReplay(self, game):
        self.gi = gi = GameInterface(self.app, game.world,
                onDisconnectRequest=self.replayOver, replay=True)
        self.agentId = game.addAgent(gi.eventPlug, gi.controller)

    def replayOver(self):
        self.elements = [self.backdrop, self.startupInterface]

    def _disconnectGame(self):
        '''
        Disconnected from the game.
        '''
        if self.netHandler is not None:
            self.netHandler.disconnect()
            self.netHandler = None
        if self.app.server and self.game == self.app.server.game:
            self.connectionLost()

    def connectionFailed(self, error):
        self.elements = [self.backdrop, self.startupInterface]
        if isinstance(error.value, ConnectionFailed):
            text = str(error.value.reason)
        else:
            text = 'Internal Error'
            print 'Unexpected failure in deferred: %s' % (error.value,)
            error.printTraceback()
        d = ConnectionFailedDialog(self.app, text)
        d.Show()

    def connectionLost(self, reason=None):
        self.elements = [self.backdrop, self.startupInterface]
        if self.game is not None:
            self.game.detachAgent(self.agentId)
        if reason is not None:
            self.gi = None
            self.game = None
            d = ConnectionFailedDialog(self.app, reason)
            d.Show()
        self.agentId = None

    def connectToReplay(self, filename):

        game, eventPlug, controlPlug = makeIsolatedGame(
                self.app.layoutDatabase)

        player = replays.ReplayPlayer(game.world, filename)        
        player.outPlug.connectPlug(eventPlug)
        
        # Would prefer something neater:
        self.setupReplay(game)
        
        player.begin()
        player.onFinished.addListener(self.connectionLost)

        self.elements = [self.gi]

