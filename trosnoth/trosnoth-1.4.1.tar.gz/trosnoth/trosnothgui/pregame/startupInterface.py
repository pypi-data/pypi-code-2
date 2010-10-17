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

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import TextElement
from trosnoth.trosnothgui.pregame.settingsMenu import SettingsMenu
from trosnoth.trosnothgui.pregame.savedGameMenu import SavedGameMenu
from trosnoth.trosnothgui.pregame.playMenu import PlayMenu
from trosnoth.trosnothgui.pregame.playscreen import PlayAuthScreen
from trosnoth.trosnothgui.pregame.playerNameMenu import PlayerNameMenu
from trosnoth.trosnothgui.pregame.common import mainButton
from trosnoth.trosnothgui.credits import CreditsScreen

from trosnoth.trosnothgui.pregame.firstplaynotify import FirstPlayNotificationBar
from trosnoth.trosnothgui.pregame.internetnotify import InternetGameNotificationBar

from trosnoth.gui.common import ScaledLocation

class StartupInterface(framework.CompoundElement):
    '''Represents the interface while the game is not connected to a server.'''

    def __init__(self, app, mainInterface):
        super(StartupInterface, self).__init__(app)
        self.interface = mainInterface

        # Create font.
        self.font = self.app.screenManager.fonts.bigMenuFont

        self.offsets = self.app.screenManager.offsets

        # Create other elements.
        self.buttons = [
            self.button('play',         self.playClicked,        (65, 225), hugeFont=True),
            self.button('play special', self.playSpecialClicked, (85, 280), smallFont=True),
            self.button('archives',     self.savedGamesClicked,  (65, 430)),
            self.button('settings',     self.settingsClicked,    (65, 500)),
            self.button('credits',      self.creditsClicked,     (65, 570)),
            self.button('exit',         self.exitClicked,        (939, 670), 'topright')
        ]
        self.firstTimeNotification = FirstPlayNotificationBar(app)
        self.internetGameNotification = InternetGameNotificationBar(app)
        self.elements = self.buttons + [self.internetGameNotification, self.firstTimeNotification]

        if app.identitySettings.firstTime:
            self.firstTimeNotification.show()

        # Create sub-menus.
        self.settingsMenu = SettingsMenu(app, onClose=self.mainMenu,
                onRestart=app.restart)
        self.savedGameMenu = SavedGameMenu(app, self)
        self.playMenu = PlayMenu(app, self)
        self.playerNameMenu = PlayerNameMenu(app)
        self.playerNameMenu.onGotName.addListener(self.gotName)
        self.creditsScreen = CreditsScreen(self.app,
                self.app.theme.colours.mainMenuColour, self.mainMenu,
                highlight=self.app.theme.colours.mainMenuHighlight)

        # Which sub-menu is currently active.
        self.currentMenu = None

    def button(self, text, onClick, pos, anchor='topleft', hugeFont=False,
            smallFont=False):
        return mainButton(self.app, text, onClick, pos, anchor, hugeFont, smallFont)

    def heading(self, caption):
        return TextElement(self.app, caption, self.font,
                ScaledLocation(1000, 60, 'topright'),
                self.app.theme.colours.headingColour)

    def playSpecialClicked(self):
        name = self.app.identitySettings.nick
        if name is None:
            self.elements = [self.playerNameMenu]
        else:
            self.gotName(name)

    def playClicked(self):
        playAuthScreen = PlayAuthScreen(self.app, onClose=self.mainMenu)
        self.elements = [playAuthScreen]
        playAuthScreen.begin()

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
        self.savedGameMenu.replayTab.populateList()
        self.elements = [self.savedGameMenu]

    def inetConnect(self, server, port):
        'Called when user selects connect from inet menu.'
        self.mainMenu()

        # Actually connect.
        self.interface.connectToServer(server, port)

    def replayConnect(self, fname):
        self.interface.connectToReplay(fname)
