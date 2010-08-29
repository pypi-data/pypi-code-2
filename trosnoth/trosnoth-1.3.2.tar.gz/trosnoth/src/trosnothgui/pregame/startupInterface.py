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

from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.trosnothgui.pregame.settingsMenu import SettingsMenu
from trosnoth.src.trosnothgui.pregame.savedGameMenu import SavedGameMenu
from trosnoth.src.trosnothgui.pregame.playMenu import PlayMenu
from trosnoth.src.trosnothgui.pregame.playerNameMenu import PlayerNameMenu
from trosnoth.src.trosnothgui.pregame.common import button
from trosnoth.src.trosnothgui.credits import CreditsScreen
from trosnoth.src.utils.getUserInfo import getName
from trosnoth.data import getPath
from trosnoth.src.utils import logging
from trosnoth.src.utils.getUserInfo import isFirstTime
from trosnoth.src.utils.utils import timeNow

from trosnoth.src.trosnothgui.pregame.firstplaynotify import FirstPlayNotificationBar
from trosnoth.src.trosnothgui.pregame.internetnotify import InternetGameNotificationBar



from trosnoth.src.gui.common import *


from twisted.internet import reactor

class StartupInterface(framework.CompoundElement):
    '''Represents the interface while the game is not connected to a server.'''

    def __init__(self, app, mainInterface):
        super(StartupInterface, self).__init__(app)
        self.interface = mainInterface

        # Create font.
        self.font = self.app.screenManager.fonts.bigMenuFont

        self.offsets = self.app.screenManager.offsets

        # Create other elements.
        self.buttons = [self.button('play',             self.playClicked,       (20, 210),      hugeFont = True),
                        self.button('recorded games',   self.savedGamesClicked, (20, 340)),
                        self.button('settings',         self.settingsClicked,   (20, 410)),
                        self.button('credits',          self.creditsClicked,    (20, 480)),
                        self.button('exit',             self.exitClicked,       (20, 690))
                        ]
        self.firstTimeNotification = FirstPlayNotificationBar(app)
        self.internetGameNotification = InternetGameNotificationBar(app)
        self.elements = self.buttons + [self.internetGameNotification, self.firstTimeNotification]

        if isFirstTime():
            self.firstTimeNotification.show()

        # Create sub-menus.
        self.settingsMenu = SettingsMenu(app, onClose=self.mainMenu,
                onRestart=app.restart)
        self.savedGameMenu = SavedGameMenu(app, self)
        self.playMenu = PlayMenu(app, self)
        self.playerNameMenu = PlayerNameMenu(app)
        self.playerNameMenu.onGotName.addListener(self.gotName)
        self.creditsScreen = CreditsScreen(self.app,
                self.app.theme.colours.mainMenuColour, self.mainMenu)

        # Which sub-menu is currently active.
        self.currentMenu = None

        self._inetGameWarning = False
        self._lastInetCheck = timeNow() + 8

    def button(self, text, onClick, pos, anchor='topleft', hugeFont=False):
        return button(self.app, text, onClick, pos, anchor, hugeFont)

    def heading(self, caption):
        return TextElement(self.app, caption, self.font,
                ScaledLocation(1000, 60, 'topright'),
                self.app.theme.colours.headingColour)

    def playClicked(self):
        name = getName()
        if name is None:
            self.elements = [self.playerNameMenu]
        else:
            self.gotName(name)

    def creditsClicked(self):
        self.creditsScreen.restart()
        self.elements = [self.creditsScreen]

    def gotName(self, name):
        self.playMenu.setName(name)
        self.playMenu.regainedFocus()
        self.elements = [self.playMenu]

    def exitClicked(self):
        # Quit the game.
        self.app.stop()

    def mainMenu(self):
        self.elements = self.buttons

    def settingsClicked(self):
        self.elements = [self.settingsMenu]

    def savedGamesClicked(self):
        self.savedGameMenu.populateList()
        self.elements = [self.savedGameMenu]

    def inetConnect(self, server, port):
        'Called when user selects connect from inet menu.'
        self.mainMenu()

        # Actually connect.
        self.interface.connectToServer(server, port)

    def replayConnect(self, fname):
        self.interface.connectToReplay(fname)

    def draw(self, screen):
        super(StartupInterface, self).draw(screen)

        # Check if the discovery protocol thinks we're on the Internet.
        t = timeNow()
        if t > self._lastInetCheck + 2:
            self_lastInetCheck = t
            if self.app.discoverer.isInternetAccessible():
                if self._inetGameWarning:
                    self._inetGameWarning = False
                    self.internetGameNotification.hide()
            else:
                if not self._inetGameWarning:
                    self._inetGameWarning = True
                    self.internetGameNotification.show()
