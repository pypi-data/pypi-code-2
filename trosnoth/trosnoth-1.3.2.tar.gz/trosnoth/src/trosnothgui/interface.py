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

'''interface.py - defines the Interface class which deals with drawing the
game to the screen, including menus and other doodads.'''

import pygame

from trosnoth.src.network.client import ClientNetHandler, ConnectionFailed
from trosnoth.src.game import makeIsolatedGame
from trosnoth.src.gamerecording import replays

from trosnoth.src.gui.framework import framework, elements

from trosnoth.src.trosnothgui.pregame.startupInterface import StartupInterface
from trosnoth.src.trosnothgui.pregame.connectingScreen import ConnectingScreen
from trosnoth.src.trosnothgui.pregame.backdrop import TrosnothBackdrop

from trosnoth.src.trosnothgui.pregame.connectionFailedDialog import ConnectionFailedDialog
from trosnoth.src.trosnothgui.ingame.gameInterface import GameInterface

class Interface(framework.CompoundElement):
    def __init__(self, app):
        super(Interface, self).__init__(app)

        # Create an interfaces for pre- and post-connection.
        self.backdrop = TrosnothBackdrop(app)
        self.startupInterface = StartupInterface(app, self)

        self._buildPointer()
        self.gi = None

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
        result.addCallback(self.connectionEstablished).addErrback(
                self.connectionFailed)
        return result

    def cancelConnecting(self, source):
        self.netHandler.cancelConnecting()
        self.startupInterface.mainMenu()

    def connectionEstablished(self, settings):
        'Called when this client establishes a connection to a server.'
        self.startupInterface.mainMenu()

        game, eventPlug, controlPlug = makeIsolatedGame(
                self.app.layoutDatabase)
        self.netHandler.requestPlug.connectPlug(controlPlug)
        self.netHandler.eventPlug.connectPlug(eventPlug)

        self.setupGame(game)
        game.syncWorld()

        self.elements = [self.gi]

    def setupGame(self, game):
        # Create a game interface.
        self.gi = gi = GameInterface(self.app, game.world,
                onDisconnectRequest=self._disconnectGame,
                onConnectionLost=self.connectionLost)
        game.addAgent(gi.eventPlug, gi.controller)

    def setupReplay(self, game):
        self.gi = gi = GameInterface(self.app, game.world,
                onDisconnectRequest=self.replayOver)
        game.addAgent(gi.eventPlug, gi.controller)

    def replayOver(self):
        self.elements = [self.backdrop, self.startupInterface]

    def _disconnectGame(self):
        '''
        Disconnected from the game.
        '''
        if self.netHandler is not None:
            self.netHandler.disconnect()
            self.netHandler = None

    def connectionFailed(self, error):
        self.elements = [self.backdrop, self.startupInterface]
        if type(error.value) == ConnectionFailed:
            text = str(error.value.reason)
        else:
            text = 'Internal Error'
            print 'Unexpected failure in deferred: %s' % (error.value,)
            error.printTraceback()
        d = ConnectionFailedDialog(self.app, text)
        d.Show()

    def connectionLost(self, reason=None):
        self.elements = [self.backdrop, self.startupInterface]
        if reason is not None:
            self.gi = None
            d = ConnectionFailedDialog(self.app, reason)
            d.Show()

    def connectToReplay(self, filename):

        game, eventPlug, controlPlug = makeIsolatedGame(
                self.app.layoutDatabase)

        player = replays.ReplayPlayer(filename)        
        player.outPlug.connectPlug(eventPlug)
        
        # Would prefer something neater:
        game.world.replay = True
        self.setupReplay(game)
        
        player.begin()
        player.onFinished.addListener(self.connectionLost)

##        client = replays.makeClient(self.app, filename)
##        world = client.world
##        client.onClosed.addListener(self.connectionLost)
##        self.setupGame(world, client)

        self.elements = [self.gi]

