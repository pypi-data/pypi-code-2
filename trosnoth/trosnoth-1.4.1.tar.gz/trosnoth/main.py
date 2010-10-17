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

# DEBUG: If this flag is set, profile information will be printed on exit.
profileMe = False

# DEBUG: If this flag is set, all game information will be saved to a log file.
logMe = False

from optparse import OptionParser

import pygame
from twisted.internet.error import CannotListenError

from trosnoth.settings import DisplaySettings, SoundSettings, IdentitySettings
from trosnoth.trosnothgui import interface
from trosnoth.themes import Theme
from trosnoth.utils import logging
from trosnoth.model.mapLayout import LayoutDatabase
from trosnoth.network.lobby import UDPMulticaster
from trosnoth.network.networkDefines import serverVersion
from trosnoth.network.server import ServerNetHandler

from trosnoth.gui import app

from trosnoth.network.netman import NetworkManager

GAME_TITLE = 'Trosnoth'
TESTMODE_AI_COUNT = 7
TESTMODE_HALF_WIDTH = 1
TESTMODE_HEIGHT = 1
BLOCKTEST_HALF_WIDTH = 2
BLOCKTEST_HEIGHT = 1

parser = OptionParser()
parser.add_option('-s', '--solo', action='store_const', dest='mode',
    const='solo', default='normal',
    help='run Trosnoth in solo mode.')
parser.add_option('-i', '--isolate', action='store_const', dest='mode',
    const='isolate',
    help='run Trosnoth in isolated test mode. Creates client and server '
    'Universe objects, but does not use the network to connect them.')
parser.add_option('-t', '--test', action='store_true', dest='testMode',
    help='run Trosnoth in test mode. This means that players will get 20 '
    'stars each and upgrades will only cost 1 star.')
parser.add_option('-c', '--checkpoint', action='store_true', dest='checkpoint',
    help='store which checkpoints have been reached.')
parser.add_option('-b', '--testblock', action='store', dest='mapBlock',
    help='tests the map block with the given filename.')
parser.add_option('-a', '--aicount', action='store', dest='aiCount',
    help='the number of AIs to include.')
parser.add_option('-w', '--halfwidth', action='store', dest='halfWidth',
    help='the half map width')
parser.add_option('-H', '--height', action='store', dest='height',
    help='the map height')
parser.add_option('-S', '--stack-teams', action='store_true', dest='stackTeams',
    help='stack all the AI players on one team.')

class Main(app.MultiWindowApplication):
    '''Instantiating the Main class will set up the game. Calling the run()
    method will run the reactor. This class handles the three steps of joining
    a game: (1) get list of clients; (2) connect to a server; (3) join the
    game.'''

    def __init__(self):
        '''Initialise the game.'''
        pygame.init()

        self.server = None
        self.serverInvisible = False
        self.initNetwork()

        self.displaySettings = DisplaySettings(self)
        self.soundSettings = SoundSettings(self)
        self.identitySettings = IdentitySettings(self)

        if self.displaySettings.fullScreen:
            options = pygame.FULLSCREEN
        else:
            options = 0

        pygame.font.init()
        super(Main, self).__init__(
            self.displaySettings.getSize(),
            options,
            GAME_TITLE,
            interface.Interface)

        # Set the master sound volume.
        self.soundSettings.apply()

        # Since we haven't connected to the server, there is no world.
        self.layoutDatabase = LayoutDatabase(self)

        # Start listening for game requests on the lan.
        self.multicaster = UDPMulticaster(self.getGames)

    def __str__(self):
        return 'Trosnoth Main Object'

    def getConsoleLocals(self):
        result = {
            'server': self.server,
        }
        try:
            result['game'] = self.interface.game
        except AttributeError:
            pass
        return result

    def initNetwork(self):
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

    def stopping(self):
        # Shut down the server if one's running.
        if self.server is not None:
            self.server.shutdown()

        self.multicaster.stop()
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

        self.screenManager.setScreenProperties(size, options, GAME_TITLE)

    def startServer(self, serverName, halfMapWidth=3, mapHeight=2,
            maxPlayers=8, gameDuration=0, invisibleGame=False, voting=True):
        if self.server is not None and self.server.running:
            return
        self.server = ServerNetHandler(self.layoutDatabase, self.netman,
                halfMapWidth, mapHeight, gameDuration*60, maxPlayers,
                gameName=serverName, voting=voting)
        self.serverInvisible = invisibleGame

        self.server.onShutdown.addListener(self._serverShutdown)
        self.netman.addHandler(self.server)

    def getGames(self):
        '''
        Called by multicast listener when a game request comes in.
        '''
        if self.server and not self.serverInvisible:
            gameInfo = {
                'name': self.server.game.name,
                'version': serverVersion,
                'port': self.netman.getTCPPort(),
            }
            return [gameInfo]
        return []

    def _serverShutdown(self):
        self.netman.removeHandler(self.server)
        self.server = None
        self.serverInvisible = False

def main():
    if logMe:
        logging.startLogging()

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error('no arguments expected')

    if options.mode == 'normal' and (options.testMode or options.mapBlock or
            options.aiCount or options.halfWidth or options.height or
            options.stackTeams):
        options.mode = 'solo'

    if options.mode == 'normal':
        mainObject = Main()
    else:
        from trosnoth import solotest
        isolate = options.mode == 'isolate'
        if options.mapBlock is None:
            mapBlocks = []
            aiCount = options.aiCount or TESTMODE_AI_COUNT
            halfWidth = options.halfWidth or TESTMODE_HALF_WIDTH
            height = options.height or TESTMODE_HEIGHT
            startInLobby = False
        else:
            mapBlocks = [options.mapBlock]
            aiCount = options.aiCount or 0
            halfWidth = options.halfWidth or BLOCKTEST_HALF_WIDTH
            height = options.height or BLOCKTEST_HEIGHT
            startInLobby = True

        mainObject = solotest.Main(isolate, testMode=options.testMode,
                mapBlocks=mapBlocks, size=(int(halfWidth), int(height)),
                aiCount=int(aiCount), lobby=startInLobby,
                stackTeams=options.stackTeams)

    try:
        mainObject.run_twisted()
    finally:
        if logMe:
            logging.endLogging()

        if options.checkpoint:
            from trosnoth.utils.checkpoint import saveCheckpoints
            saveCheckpoints()

if __name__ == '__main__':
    if profileMe:
        import cProfile as profile
        profile.run('main()')
        raw_input('Press enter:')
    else:
        main()
