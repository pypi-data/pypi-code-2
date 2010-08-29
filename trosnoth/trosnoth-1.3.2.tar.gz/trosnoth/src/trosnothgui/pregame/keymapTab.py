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


from trosnoth.src.trosnothgui.pregame.common import button
from trosnoth.src.gui.framework import prompt
from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.common import ScaledLocation, ScaledArea
from trosnoth.src.gui import keyboard
from trosnoth.src import keymap
from trosnoth.data import getPath, user
from trosnoth.src.utils.event import Event


class KeymapTab(Tab):

    def __init__(self, app, onClose=None):
        super(KeymapTab, self).__init__(app, 'Controls')
        self.font = app.screenManager.fonts.bigMenuFont

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        # Break things up into categories
        movement = ['jump', 'down', 'left', 'right']
        menus =    ['menu', 'more actions']
        actions =  ['respawn', 'buy upgrade',
                    'abandon', 'captain', 'team ready']
        misc =     ['chat', 'follow']
        upgrades = ['turret', 'shield', 'minimap disruption', 'phase shift',
                    'grenade', 'ricochet']
        display =  ['leaderboard', 'toggle interface', 'toggle terminal']

        actionNames = { 'abandon': 'Abandon upgrade',
                        'buy upgrade': 'Buy upgrade',
                        'captain': 'Become captain',
                        'chat': 'Chat',
                        'down': 'Drop down',
                        'follow': 'Auto pan (replay)',
                        'grenade': 'Grenade',
                        'jump': 'Jump',
                        'leaderboard': 'Show leaderboard',
                        'left': 'Move left',
                        'menu': 'Main menu',
                        'minimap disruption': 'Minimap disruption',
                        'more actions': 'Advanced',
                        'phase shift': 'Phase shift',
                        'respawn': 'Respawn',
                        'ricochet': 'Ricochet',
                        'right': 'Move right',
                        'shield': 'Shield',
                        'status bar': 'Status bar',
                        'team ready': 'Team ready',
                        'timer': 'Show timer',
                        'toggle interface': 'Toggle HUD',
                        'toggle terminal': 'Toggle terminal',
                        'turret': 'Turret',
                        'zone progress': 'Show zone bar'}

        # Organise the categories by column
        self.layout = [ [movement, menus], [actions, display], [upgrades, misc] ]

        self.errorInfo = TextElement(self.app, '', self.font,
                                 ScaledLocation(512, 580, 'center'))
        self.text = [
                     self.errorInfo
                    ]
                     
        self.inputLookup = {}

        xPos = 190

        # Lay everything out automatically.
        keymapFont = self.app.screenManager.fonts.keymapFont
        keymapInputFont = self.app.screenManager.fonts.keymapInputFont
        for column in self.layout:               # Each column
            yPos = 250
            for category in column:         # Each category
                for action in category:     # Each action
                    # Draw action name (eg. Respawn)
                    self.text.append(TextElement(self.app, actionNames[action],
                                    keymapFont,
                                    ScaledLocation(xPos, yPos,'topright'),
                                    self.app.theme.colours.headingColour
                                    ))

                    # Create input box
                    box = prompt.KeycodeBox(self.app, ScaledArea(xPos+10, yPos, 100, 30),
                                    font = keymapInputFont)
                    box.onClick.addListener(self.setFocus)
                    box.onChange.addListener(self.inputChanged)
                    box.__action = action
                    self.inputLookup[action] = box

                    yPos += 35  # Between items
                yPos += 35      # Between categories
            xPos += 320         # Between columns

        self.elements = self.text + self.inputLookup.values() + \
                        [button(app, 'restore default controls',
                                self.restoreDefaults,
                                (0, -125), 'midbottom'),
                         button(app, 'save',
                                self.saveSettings,
                                (-100, -75), 'midbottom'),
                         button(app, 'cancel',
                                self.cancel,
                                (100, -75), 'midbottom'),
                         ]
        
        self.populateInputs()
        
    def inputChanged(self, box):
        # Remove the old key.
        try:
            oldKey = self.keyMapping.getkey(box.__action)
        except KeyError:
            pass
        else:
            del self.keyMapping[oldKey]

        # Set the new key.
        self.keyMapping[box.value] = box.__action

        # Refresh the display.
        self.refreshInputs()

    def populateInputs(self):
        # Set up the keyboard mapping.
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)

        try:
            # Try to load keyboard mappings from the user's personal settings.
            config = open(getPath(user, 'keymap'), 'rU').read()
            self.keyMapping.load(config)
        except IOError:
            pass

        # Refresh the display.
        self.refreshInputs()

    def refreshInputs(self):
        for column in self.layout:
            for category in column:
                for action in category:
                    # Get the current key and put it in the box.
                    try:
                        key = self.keyMapping.getkey(action)
                    except KeyError:
                        key = None
                    self.inputLookup[action].value = key

                    # Make the box white
                    self.inputLookup[action].backColour = (255,255,255)

    def restoreDefaults(self):
        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)
        self.refreshInputs()

        self.incorrectInput("Default controls restored: press 'save' to confirm", (0,128,0))
    
    def clearBackgrounds(self):
        for action in self.inputLookup:
            self.inputLookup[action].backColour = (255,255,255)
        self.setFocus(None)

    def saveSettings(self):
        # Perform the save.
        open(getPath(user, 'keymap'), 'w').write(self.keyMapping.save())

        emptyBoxes = []

        for box in self.inputLookup.itervalues():
            if box.value is None:
                emptyBoxes.append(box)
            
        if len(emptyBoxes) > 0:
            self.populateInputs()
            for box in emptyBoxes:
                box.backColour = self.app.theme.colours.invalidDataColour

            self.incorrectInput('Warning: some actions have no key', (192, 0, 0))
        else:
            self.mainMenu()

    def incorrectInput(self, string, colour):
        self.errorInfo.setColour(colour)
        self.errorInfo.setText(string)
        self.errorInfo.setFont(self.font)

    def cancel(self):
        self.populateInputs()
        self.mainMenu()

    def mainMenu(self):
        self.incorrectInput('', (0,0,0))
        self.clearBackgrounds()
        self.onClose.execute()
