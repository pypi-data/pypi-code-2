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

import pygame
from trosnoth.src.ai import AlphaAI
from trosnoth.src.gamerecording.gamerecorder import GameRecorder
from trosnoth.src.game import makeLocalGame, makeIsolatedGame
from trosnoth.src.gui import app
from trosnoth.src.settings import DisplaySettings, SoundSettings
from trosnoth.src.themes import Theme
from trosnoth.src.trosnothgui import defines
from trosnoth.src.trosnothgui.ingame.gameInterface import GameInterface
from trosnoth.src.gui.framework import framework
from trosnoth.src.model import mapLayout

SIZE = 1,1
AI_PLAYERS = 7

class Main(app.MultiWindowApplication):
    def __init__(self, isolate=False, size=SIZE, aiCount=AI_PLAYERS,
            mapBlocks=(), testMode=False):
        '''Initialise the game.'''
        self.size = size
        self.aiCount = aiCount
        self.isolate = isolate
        self.mapBlocks = mapBlocks
        self.testMode = testMode

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)

        if self.displaySettings.fullScreen:
            options = pygame.locals.FULLSCREEN
        else:
            options = 0

        pygame.font.init()
        super(Main, self).__init__(
            self.displaySettings.getSize(),
            options,
            defines.gameName,
            SoloInterface)

        # Set the master sound volume.
        self.soundSettings.apply()

        # Since we haven't connected to the server, there is no world.
        self.player = None
        self.startGame()

    def initialise(self):
        super(Main, self).initialise()

        # Loading the theme loads the fonts.
        self.theme = Theme(self)

    def getFontFilename(self, fontName):
        '''
        Tells the UI framework where to find the given font.
        '''
        return self.theme.getPath('fonts', fontName)

    def changeScreenSize(self, size, fullScreen):
        if fullScreen:
            options = pygame.locals.FULLSCREEN
        else:
            options = 0

        self.screenManager.setScreenProperties(size, options, defines.gameName)

    def startGame(self):
        db = mapLayout.LayoutDatabase(self, blocks=self.mapBlocks)
        self.game = game = makeLocalGame(db)
        layout = db.generateRandomMapLayout(*self.size)
        game.world.setLayout(layout)
        if self.testMode:
            game.world.setTestMode()
            

        # Create a client and an interface.
        if self.isolate:
            igame, eventPlug, controlPlug = makeIsolatedGame(db)
            self.igame = igame
            self.gi = gi = GameInterface(self, igame.world)
            game.addAgent(eventPlug, controlPlug)
            igame.addAgent(gi.eventPlug, gi.controller)
            igame.syncWorld()
        else:
            self.gi = gi = GameInterface(self, game.world)
            game.addAgent(gi.eventPlug, gi.controller)
        gi.onDisconnectRequest.addListener(self.stop)
        gi.onConnectionLost.addListener(self.stop)
        self.interface.elements.append(gi)
        from trosnoth.src.network.networkDefines import serverVersion
        gameRecorder = GameRecorder('Solo Trosnoth', serverVersion, game.world)
        self.gameRecorder = gameRecorder
        game.addAgent(gameRecorder.inPlug, gameRecorder.outPlug)
        gameRecorder.begin()

        for i in xrange(self.aiCount):
            ai = AlphaAI(game.world)
            game.addAgent(ai.eventPlug, ai.requestPlug)
            ai.start()

    def stop(self):
        if self.gameRecorder is not None:
            self.gameRecorder.stop()
            self.gameRecorder = None
        super(Main, self).stop()

class SoloInterface(framework.CompoundElement):
    def __init__(self, app):
        super(SoloInterface, self).__init__(app)
        self.elements = []
