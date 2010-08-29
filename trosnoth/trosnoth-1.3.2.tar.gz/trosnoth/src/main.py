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

# DEBUG: If this flag is set, profile information will be printed on exit.
profileMe = False

# DEBUG: If this flag is set, all game information will be saved to a log file.
logMe = False

import sys, pygame
from twisted.internet.error import CannotListenError

from trosnoth.src.settings import DisplaySettings, SoundSettings
from trosnoth.src.trosnothgui import interface
from trosnoth.src.themes import Theme
from trosnoth.src.trosnothgui import defines
from trosnoth.src.utils import logging
from trosnoth.src.model.mapLayout import LayoutDatabase
from trosnoth.src.network.networkDefines import serverVersion
from trosnoth.src.network.server import ServerNetHandler
from trosnoth.src.gamerecording.gamerecorder import GameRecorder

from trosnoth.src.gui import app

from trosnoth.src.network.netman import NetworkManager
from trosnoth.src.network.trosnothdiscoverer import TrosnothDiscoverer


class Main(app.MultiWindowApplication):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''

    def __init__(self):
        '''Initialise the game.'''

        self.initNetwork()

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
            interface.Interface)

        # Set the master sound volume.
        self.soundSettings.apply()

        # Since we haven't connected to the server, there is no world.
        self.player = None
        self.layoutDatabase = LayoutDatabase(self)

        self.gameRecorder = None

    def __str__(self):
        return 'Trosnoth Main Object'

    def initNetwork(self):
        self.server = None

        # Set up the network connection.
        try:
            self.netman = NetworkManager(6789, 6789)
        except CannotListenError:
            # Set up a network manager on an arbitrary port (i.e.
            # you probably cannot run an Internet server because you
            # won't have port forwarding for the correct port.)
            self.netman = NetworkManager(0, None)

            # TODO: Perhaps show a message on the interface warning that games
            # may not be visible on the Internet.

        # Set up the game discovery protocol.
        self.discoverer = TrosnothDiscoverer(self.netman)

    def stopping(self):
        # Shut down the server if one's running.
        if self.server is not None:
            self.server.shutdown()

        # Save the discoverer's peers.
        self.discoverer.kill()

        super(Main, self).stopping()

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

    def startServer(self, serverName, halfMapWidth=3, mapHeight=2,
                    maxPlayers=8, gameDuration=0, recordReplay=None,
                    invisibleGame=False):
        if self.server is not None and self.server.running:
            return
        self.server = ServerNetHandler(self.layoutDatabase, self.netman,
                halfMapWidth, mapHeight, gameDuration*60, maxPlayers)
        
        if recordReplay:
            game = self.server.game
            gameRecorder = GameRecorder(serverName, serverVersion, game.world)
            self.gameRecorder = gameRecorder
            game.addAgent(gameRecorder.inPlug, gameRecorder.outPlug)
            gameRecorder.begin()

        # Tell the discovery protocol about it.
        if not invisibleGame:
            info = {
                'name': serverName,
                'version': serverVersion,
            }
            self.discoverer.setGame(info)
            self.server.onShutdown.addListener(self._serverShutdown)
            self.netman.addHandler(self.server)

    def _serverShutdown(self):
        self.discoverer.delGame()
        if self.gameRecorder is not None:
            self.gameRecorder.stop()
            self.gameRecorder = None
        self.netman.removeHandler(self.server)
        self.server = None

def runGame():
    if logMe:
        logging.startLogging()
    
    if '--isolate' in sys.argv:
        # For testing.
        from trosnoth.src import solotest
        mainObject = solotest.Main(True)
    elif '--test' in sys.argv:
        # For testing
        from trosnoth.src import solotest
        mainObject = solotest.Main(testMode=True)
    elif '--solo' in sys.argv:
        # For testing.
        from trosnoth.src import solotest
        mainObject = solotest.Main()
    else:
        mainObject = Main()

    try:
        mainObject.run_twisted()
    finally:
        if logMe:
            logging.endLogging()

        if 'checkpoint' in sys.argv:
            from trosnoth.src.utils.checkpoint import saveCheckpoints
            saveCheckpoints()

if __name__ == '__main__':
    if profileMe:
        import cProfile as profile
        profile.run('runGame()')
        raw_input('Press enter:')
    else:
        runGame()
