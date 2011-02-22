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

import pygame

from trosnoth.utils.utils import timeNow
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.hint import Hint
import trosnoth.gui.framework.prompt as prompt
from trosnoth.gui.framework.elements import TextElement, TextButton
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework.checkbox import CheckBox
from trosnoth.gui.framework.dialogbox import (DialogBox, DialogResult,
        DialogBoxAttachedPoint)
from trosnoth.data import startupMenu

from trosnoth.gui.common import (Location, ScaledSize, ScaledArea,
        ScaledLocation, SizedImage)

from trosnoth.trosnothgui.pregame.imageRadioButton import (ImageRadioButton,
        RadioButtonGroup)
from trosnoth.utils.twist import WeakCallLater, WeakLoopingCall

from trosnoth.data import getPath

log = logging.getLogger('serverSetubTab')

MAX_TEAM_NAME_LENGTH = 10

class ServerSetupTab(Tab):
    def __init__(self, app, tabContainer):
        super(ServerSetupTab, self).__init__(app, 'Start a Game')
        self.tabContainer = tabContainer
        self.toCreate = ServerDoesntExistMenu(app, tabContainer, self)
        self.created = ServerAlreadyExistsMenu(app, tabContainer, self)
        self.setAppropriateElements()

        # Refresh the elements list every now and then in case server has shut
        # down.
        self._lastUpdate = timeNow()

    def setAppropriateElements(self):
        if self.app.server is not None:
            self.elements = [self.created]
            self.tabContainer.renameTab('Game Options', self)
        else:
            self.elements = [self.toCreate]
            self.tabContainer.renameTab('Start a Game', self)

    def setName(self, name):
        self.toCreate.setName(name)

    def draw(self, screen):
        # Automatically update every half second, but only lazily in case it's
        # not visible.
        time = timeNow()
        if self._lastUpdate < time - 0.5:
            self.setAppropriateElements()
            self._lastUpdate = time

        super(ServerSetupTab, self).draw(screen)

class ServerDoesntExistMenu(framework.TabFriendlyCompoundElement):
    def __init__(self, app, tabContainer, parent):
        super(ServerDoesntExistMenu, self).__init__(app)
        self.tabContainer = tabContainer
        self.parent = parent

        self.serverName = ''
        self.mapHeight = ''
        self.halfMapWidth = ''
        self.maxPlayers = ''

        font = self.app.screenManager.fonts.bigMenuFont

        self.radio = RadioButtonGroup(app)

        imageSize = ScaledSize(200, 120)
        imageSmall = SizedImage(getPath(startupMenu, 'small.png'), imageSize,
                (0, 0, 0))
        imageLong  = SizedImage(getPath(startupMenu, 'long.png'), imageSize,
                (0, 0, 0))
        imageLarge = SizedImage(getPath(startupMenu, 'large.png'), imageSize,
                (0, 0, 0))

        largeRadio = ImageRadioButton(app, 'Standard',
                ScaledArea(85, 370, 200, 150), imageLarge)
        largeRadio.value = (3, 2)
        self.radio.add(largeRadio)

        smallRadio = ImageRadioButton(app, 'Small', ScaledArea(305,
                370, 200, 150), imageSmall)
        smallRadio.value = (1, 1)
        self.radio.add(smallRadio)

        longRadio = ImageRadioButton(app, 'Wide', ScaledArea(85, 540, 200, 150),
                imageLong)
        longRadio.value = (5, 1)
        self.radio.add(longRadio)

        self.customRadio = ImageRadioButton(app, 'Custom',
                ScaledArea(305,540,200,150), None)
        self.radio.add(self.customRadio)

        self.customOne = prompt.InputBox(self.app, ScaledArea(390, 605, 40, 60,
                'midright'), initValue='2', maxLength=1,
                font=self.app.screenManager.fonts.hugeMenuFont,
                validator=prompt.intValidator)
        self.customOne.onClick.addListener(self.setFocus)
        self.customOne.onClick.addListener(self.selectCustomRadio)
        self.customOne.onTab.addListener(self.customTab)
        self.customOne.onEnter.addListener(self.startServer)
        self.customOne.onEdit.addListener(self.customUpdated)

        self.customTwo = prompt.InputBox(self.app, ScaledArea(422, 605, 40, 60,
                'midleft'), initValue='1', maxLength=1,
                font=self.app.screenManager.fonts.hugeMenuFont,
                validator=prompt.intValidator)
        self.customTwo.onClick.addListener(self.setFocus)
        self.customTwo.onClick.addListener(self.selectCustomRadio)
        self.customTwo.onTab.addListener(self.customTab)
        self.customTwo.onEnter.addListener(self.startServer)
        self.customTwo.onEdit.addListener(self.customUpdated)

        self.customRadio.value = (int(self.customOne.value),
                int(self.customTwo.value))

        self.custom = [
            TextElement(self.app, 'x',
                self.app.screenManager.fonts.hugeMenuFont, ScaledLocation(405,
                605, 'center'), self.app.theme.colours.black),
            self.customOne,
            self.customTwo,
        ]

        self.radio.selected(largeRadio)
        self.radio.onSelectionChanged.addListener(self.setSelectionNumber)

        colours = app.theme.colours
        self.text = [
            TextElement(self.app, 'Game Name:', font, ScaledLocation(85, 220),
                    colours.headingColour),
            TextElement(self.app, 'Team Size:', font, ScaledLocation(600, 220),
                    colours.headingColour),
            TextElement(self.app, 'players per side',
                    app.screenManager.fonts.smallNoteFont, ScaledLocation(720,
                    295), colours.headingColour),
            TextElement(self.app, 'Time Limit:', font, ScaledLocation(600, 360),
                    colours.headingColour),
            TextElement(self.app, 'minutes', app.screenManager.fonts.menuFont,
                    ScaledLocation(720, 435), colours.headingColour),
        ]

        self.invalidInputText = TextElement(self.app, '',
                self.app.screenManager.fonts.ampleMenuFont, ScaledLocation(50,
                770, 'bottomleft'), colours.invalidDataColour)
        self.serverInput = prompt.InputBox(self.app, ScaledArea(85, 275, 420,
                60), initValue='', font=font)
        self.serverInput.onClick.addListener(self.setFocus)
        self.serverInput.onTab.addListener(self.tabNext)
        self.serverInput.onEnter.addListener(self.startServer)

        self.maxPlayersInput = prompt.InputBox(self.app, ScaledArea(600, 275,
                100, 60), initValue='10', font=font, maxLength=3,
                validator=prompt.intValidator)
        self.maxPlayersInput.onClick.addListener(self.setFocus)
        self.maxPlayersInput.onTab.addListener(self.tabNext)
        self.maxPlayersInput.onEnter.addListener(self.startServer)

        self.gameDurationInput = prompt.InputBox(self.app, ScaledArea(600, 415,
                100, 60), initValue='45', font=font, maxLength=3,
                validator=prompt.intValidator)
        self.gameDurationInput.onClick.addListener(self.setFocus)
        self.gameDurationInput.onTab.addListener(self.tabNext)
        self.gameDurationInput.onEnter.addListener(self.startServer)

        self.noLimitBox = CheckBox(self.app, ScaledLocation(830, 368),
                text='No Limit', font=app.screenManager.fonts.smallNoteFont,
                colour=colours.secondMenuColour, initValue=False,
                style='circle')
        self.noLimitBox.onValueChanged.addListener(lambda sender:
                self.enableGameDuration(not sender.value))

        self.invisibleGameBox = CheckBox(self.app, ScaledLocation(600, 520),
                text='Invisible game',
                font=app.screenManager.fonts.smallNoteFont,
                colour=colours.secondMenuColour, initValue=False,
                style='circle')

        igHint = Hint(app, 'Others will need to know your IP address to '
                'connect.', self.invisibleGameBox,
                font=app.screenManager.fonts.smallNoteFont)


        self.startButton = TextButton(self.app, ScaledLocation(600, 610),
                'start', app.screenManager.fonts.hugeMenuFont,
                colours.startButton, colours.white)
        self.startButton.onClick.addListener(self.startServer)

        self.input = [self.serverInput, self.maxPlayersInput,
                self.gameDurationInput]
        self.enableGameDuration(True)

        self.elements = self.text + self.input + [
            self.invisibleGameBox,
            self.noLimitBox,
            self.invalidInputText,
            self.startButton,
            self.radio,
            igHint
        ] + self.custom
        self.setFocus(self.serverInput)
        self.lastSelection = -1
        self.setSelectionNumber(0)

    def customTab(self, sender):
        if sender == self.customOne:
            self.setFocus(self.customTwo)
        else:
            self.setFocus(self.customOne)

    def setSelectionNumber(self, index):
        playerSizes = [10, 4, 6]
        timeLimits = [45, 10, 20]
        chosenNum = int(self.maxPlayersInput.getValue())
        if (self.lastSelection == -1 or self.lastSelection == 3 or
                playerSizes[self.lastSelection] == chosenNum) and index != 3:
            self.maxPlayersInput.setValue(str(playerSizes[index]))
        if not self.noLimitBox.value:
            chosenLimit = int(self.gameDurationInput.getValue())
            if ((self.lastSelection == -1 or self.lastSelection == 3 or
                    timeLimits[self.lastSelection] == chosenLimit) and
                    index != 3):
                self.gameDurationInput.setValue(str(timeLimits[index]))

        if index != 3 and index != -1:
            self.lastSelection = index


    def setName(self, name):
        #if self.serverInput.getValue() == '':
            self.serverInput.setValue("%s's game" % (name,))

    def setTabOrder(self):
        if self._enableGameDuration:
            self.tabOrder = [self.serverInput, self.maxPlayersInput,
                    self.gameDurationInput]
        else:
            self.tabOrder = [self.serverInput, self.maxPlayersInput]

    def selectCustomRadio(self, object):
        self.customRadio._clicked()
        self.customUpdated(object)

    def customUpdated(self, object):
        if self.customOne.value != '' and self.customTwo.value != '':
            self.customRadio.value = (int(self.customOne.value),
                    int(self.customTwo.value))
        else:
            self.customRadio.value = None

    def setFocus(self, object):
        if (not self._enableGameDuration) and object == self.gameDurationInput:
            self.noLimitBox.setValue(False)
        hadFocus = self.gameDurationInput.hasFocus
        super(ServerDoesntExistMenu, self).setFocus(object)
        # If the game duration box had and now does not have focus
        if (hadFocus and not self.gameDurationInput.hasFocus and
                self.gameDurationInput.value == ''):
            self.enableGameDuration(False)
            self.noLimitBox.setValue(True)

    def enableGameDuration(self, val):
        self._enableGameDuration = val
        if val:
            self.gameDurationInput.setBackColour(self.app.theme.colours.white)
            self.setFocus(self.gameDurationInput)
        else:
            self.gameDurationInput.setBackColour(
                    self.app.theme.colours.disabled)
            if self.gameDurationInput.hasFocus:
                self.setFocus(self.maxPlayersInput)
        self.setTabOrder()


    def startServer(self, sender):
        values = self.getValues()
        if values is not None:
            self.incorrectInput('')
            self.app.startServer(**values)
            self.parent.setAppropriateElements()
            # Select the LAN tab
            self.tabContainer.selectTab(0)
            # Set the server name back to nothing in case
            # the user changes their player name in-game -
            # it will be reset hereafter.

    def setBackColours(self):
        if self._enableGameDuration:
            self.gameDurationInput.setBackColour(self.app.theme.colours.white)
        else:
            self.gameDurationInput.setBackColour(
                    self.app.theme.colours.disabled)
        self.maxPlayersInput.setBackColour(self.app.theme.colours.white)
        self.serverInput.setBackColour(self.app.theme.colours.white)
        self.customOne.setBackColour(self.app.theme.colours.white)
        self.customTwo.setBackColour(self.app.theme.colours.white)

    def getValues(self):
        '''
        Returns the inputted values in the order:
        1. halfMapWidth
        2. mapHeight
        3. maxPlayers
        4. Game Duration
        5. Record Replay?
        6. Invisible game?
        '''
        numPlayers = (2, 128)

        self.setBackColours()

        invalid = False

        colours = self.app.theme.colours
        height = width = maxPlayers = duration = name = None
        if self.serverInput.value == '':
            if not invalid:
                invalid = True
            self.serverInput.setBackColour(colours.invalidDataColour)
        else:
            name = self.serverInput.value

        if (numPlayers[0] <= self.getInt(self.maxPlayersInput.value) <=
                numPlayers[1]):
            maxPlayers = self.getInt(self.maxPlayersInput.value)
        else:
            if not invalid:
                invalid = True
            self.maxPlayersInput.setBackColour(colours.invalidDataColour)


        if self.noLimitBox.value:
            duration = 0
        else:
            duration = self.getInt(self.gameDurationInput.value)
            if duration == 0:
                self.gameDurationInput.setBackColour(colours.invalidDataColour)
                if not invalid:
                    invalid = True

        radioChoice = self.radio.getSelectedValue()
        if radioChoice is None:
            if not invalid:
                invalid = True
                self.customOne.setBackColour(colours.invalidDataColour)
                self.customTwo.setBackColour(colours.invalidDataColour)

        if invalid:
            return None

        invisible = self.invisibleGameBox.value
        width, height = radioChoice

        return dict(serverName=name, halfMapWidth=width, mapHeight=height,
                maxPlayers=maxPlayers, gameDuration=duration,
                invisibleGame=invisible, voting=False)

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)


    def incorrectInput(self, string):
        self.invalidInputText.setText(string)

    def draw(self, surface):
        super(ServerDoesntExistMenu, self).draw(surface)
        rect = self.tabContainer._getTabRect()
        verLineX = rect.left + (rect.width * 0.545)
        colour = self.app.theme.colours.tabContainerColour
        pygame.draw.line(surface, colour, (verLineX, rect.top), (verLineX,
                rect.bottom), self.tabContainer._getBorderWidth())
        horLineY = rect.top + (rect.height * 0.72)
        pygame.draw.line(surface, colour, (verLineX, horLineY), (rect.right,
                horLineY), self.tabContainer._getBorderWidth())

        pygame.draw.rect(surface, self.app.theme.colours.black,
                         self.customOne._getRect(), 1)
        pygame.draw.rect(surface, self.app.theme.colours.black,
                         self.customTwo._getRect(), 1)


class ServerAlreadyExistsMenu(framework.TabFriendlyCompoundElement):
    def __init__(self, app, tabContainer, parent):
        super(ServerAlreadyExistsMenu, self).__init__(app)
        self.tabContainer = tabContainer
        self.parent = parent

        self.blueTeamName = 'Blue'
        self.redTeamName = 'Red'
        self.gameMode = 'Normal'

        self.inputsEdited = False
        self.resetCountdownDefault = 30
        self.resetCountdown = self.resetCountdownDefault
        self.resetTimer = WeakLoopingCall(self, 'resetCountdownFunction')

        self.delayedCall = None
        self._lastStatusUpdate = timeNow()

        font = self.app.screenManager.fonts.bigMenuFont
        colours = app.theme.colours

        # Static text
        self.staticText = [
            TextElement(self.app, 'Game Status:', font, ScaledLocation(70, 255),
                    colours.headingColour),
            TextElement(self.app, 'Team Names:', font, ScaledLocation(70, 335),
                    colours.headingColour),
            TextElement(self.app, 'Game Mode:', font, ScaledLocation(70, 415),
                    colours.headingColour)]

        # Dynamic text
        self.assistanceText = TextElement(self.app, '', font, ScaledLocation(70,
                490), colours.invalidDataColour)
        self.gameStatusText = TextElement(self.app, 'Not yet started', font,
                ScaledLocation(350, 255), colours.inactive)

        self.dynamicText = [self.assistanceText, self.gameStatusText]

        # Input boxes
        self.blueTeamInput = prompt.InputBox(self.app, ScaledArea(350, 320, 270,
                60), initValue=self.blueTeamName, font=font,
                colour=colours.blueTeamSetup, maxLength=MAX_TEAM_NAME_LENGTH)
        self.blueTeamInput.onClick.addListener(self.setFocus)
        self.blueTeamInput.onEdit.addListener(lambda sender: self.inputEdit())
        self.blueTeamInput.onTab.addListener(self.tabNext)
        self.blueTeamInput.onEnter.addListener(lambda sender:
                self.saveSettings())

        self.redTeamInput = prompt.InputBox(self.app, ScaledArea(655, 320, 270,
                60), initValue=self.redTeamName, font=font,
                colour=colours.redTeamSetup, maxLength=MAX_TEAM_NAME_LENGTH)
        self.redTeamInput.onClick.addListener(self.setFocus)
        self.redTeamInput.onEdit.addListener(lambda sender: self.inputEdit())
        self.redTeamInput.onTab.addListener(self.tabNext)
        self.redTeamInput.onEnter.addListener(lambda sender:
                self.saveSettings())

        self.gameModeInput = prompt.InputBox(self.app, ScaledArea(350, 400, 575,
                60), initValue=self.gameMode, font=font, colour=colours.white,
                maxLength=20)
        self.gameModeInput.onClick.addListener(self.setFocus)
        self.gameModeInput.onEdit.addListener(lambda sender: self.inputEdit())
        self.gameModeInput.onTab.addListener(self.tabNext)
        self.gameModeInput.onEnter.addListener(lambda sender:
                self.saveSettings())

        self.input = self.tabOrder = [self.blueTeamInput, self.redTeamInput,
                self.gameModeInput]

        # Text buttons
        self.shutdownButton = TextButton(self.app, ScaledLocation(410, 645,
                'center'), 'Shut Down Server',
                app.screenManager.fonts.hugeMenuFont, colours.noGamesColour,
                colours.white)
        self.shutdownButton.onClick.addListener(lambda sender:
                self.shutdownServer())
        self.shutdownWarning = False

        self.startGameButton = TextButton(self.app, ScaledLocation(925, 255,
                'topright'), 'force begin', font, colours.secondMenuColour,
                colours.white)
        self.startGameButton.onClick.addListener(lambda sender:
                self.startGame())

        self.saveButton = TextButton(self.app, ScaledLocation(925, 490,
                'topright'), 'save settings', font, colours.secondMenuColour,
                colours.white)
        self.saveButton.onClick.addListener(lambda sender: self.saveSettings())

        self.buttons = [self.shutdownButton, self.startGameButton,
                self.saveButton]

        # By your powers combined, I am Captain Planet!
        self.elements = (self.staticText + self.dynamicText + self.input +
                self.buttons)

        self.updateStatus()

    def saveSettings(self):
        colours = self.app.theme.colours
        cmd = self.getCmdInterface()
        if cmd is None:
            self.assistanceText.setText('Game is not running!')
            self.assistanceText.setColour(colours.invalidDataColour)
            self.inputEdit()
            self.delayedErase(self.assistanceText)
            return

        blueName = self.blueTeamInput.getValue().strip()
        if blueName != self.blueTeamName:
            cmd.setTeamName(0, blueName)

        redName = self.redTeamInput.getValue().strip()
        if redName != self.redTeamName:
            cmd.setTeamName(1, redName)

        gameMode = self.gameModeInput.getValue().strip()
        if gameMode != self.gameMode:
            success = cmd.setGameMode(gameMode)
        else:
            success = True

        if not success:
            self.assistanceText.setText('Invalid game mode!')
            self.assistanceText.setColour(colours.invalidDataColour)
            self.inputEdit()
        else:
            self.stopCountdown('Settings have been saved.')
            self.assistanceText.setColour(colours.startButton)
        self.delayedErase(self.assistanceText)

    def startGame(self):
        cmd = self.getCmdInterface()
        if cmd is not None:
            cmd.startGame()

    def shutdownServer(self):
        self.shutdownConfirmationBox = ShutdownDialog(self.app)
        self.shutdownConfirmationBox.onClose.addListener(self._shutdownDlgClose)
        self.shutdownConfirmationBox.show()

    def _shutdownDlgClose(self):
        if self.shutdownConfirmationBox.result == DialogResult.OK:
            if self.app.server is not None:
                self.app.server.shutdown()

    # The following three functions are all related: if a user edits the team
    # names or gamde mode but doesn't save them, they will get a certain amount
    # of time before the inputs are reset to those obtained from the server.

    def inputEdit(self):
        if (self.blueTeamInput.getValue().strip() != self.blueTeamName or
                self.redTeamInput.getValue().strip() != self.redTeamName or
                self.gameModeInput.getValue().strip() != self.gameMode):
            if not self.inputsEdited:
                self.inputsEdited = True
                self.resetTimer.start(1.0, False)
        else:
            self.stopCountdown('')

    def resetCountdownFunction(self):
        try:
            self._resetCountdownFunction()
        except Exception, e:
            log.exception(str(e))

    def _resetCountdownFunction(self):
        self.resetCountdown -= 1
        if self.resetCountdown <= 0:
            self.stopCountdown('Settings reset due to inactivity')
            self.populateInputs()
            self.delayedErase(self.assistanceText)
        elif (self.resetCountdown <= 5 or self.resetCountdown == 10 or
                self.resetCountdown == 20):
            if self.resetCountdown == 1:
                _noun = "second"
            else:
                _noun = "seconds"
            self.assistanceText.setText('Settings will reset in %d %s' %
                    (self.resetCountdown, _noun))
            self.assistanceText.setColour(self.app.theme.colours.startButton)

    def stopCountdown(self, message):
        self.assistanceText.setText(message)
        self.assistanceText.setColour(self.app.theme.colours.invalidDataColour)
        # There's a chance that the timer might never have been started.
        try:
            self.resetTimer.stop()
        except AssertionError:
            pass
        self.inputsEdited = False
        self.resetCountdown = self.resetCountdownDefault

    def populateInputs(self):
        self.blueTeamInput.setValue(self.blueTeamName)
        self.redTeamInput.setValue(self.redTeamName)
        self.gameModeInput.setValue(self.gameMode)

    def delayedErase(self, element, time = 3):
        self.delayedCall = WeakCallLater(time, self, 'clearText', element)

    def clearText(self, element):
        element.setText('')

    def getCmdInterface(self):
        if self.app.server is not None:
            return self.app.server.game

        self.parent.setAppropriateElements()
        return None

    def updateStatus(self):
        colours = self.app.theme.colours
        status = self.gameStatusText
        cmd = self.getCmdInterface()
        if cmd is None:
            return

        currentGameState = cmd.getGameState()

        if currentGameState != 'P':
            self.startGameButton.setText('')

        if currentGameState == 'P':
            status.setText('Not yet started')
            status.setColour(colours.inactive)
            self.startGameButton.setText('force begin')
        elif currentGameState == 'I':
            blueScore, redScore = cmd.getOrbCounts()

            if blueScore > redScore:
                status.setText('In progress (%d-%d to %s)' %
                        (blueScore, redScore, self.blueTeamName))
                status.setColour(colours.blueTeamSetup)
            elif redScore > blueScore:
                status.setText('In progress (%d-%d to %s)' %
                        (redScore, blueScore, self.redTeamName))
                status.setColour(colours.redTeamSetup)
            else:
                status.setText('In progress (%d-%d tie)' %
                        (redScore, blueScore))
                status.setColour(colours.bothTeams)
        elif currentGameState in ('D', 'B', 'R'):
            if currentGameState == 'B':
                status.setText('Game over - %s win!' % self.blueTeamName)
                status.setColour(colours.blueTeamSetup)
            elif currentGameState == 'R':
                status.setText('Game over - %s win!' % self.redTeamName)
                status.setColour(colours.redTeamSetup)
            else:
                status.setText('Game over - it was a draw!')
                status.setColour(colours.bothTeams)
            self.saveButton.setText('')
        else:
            self.gameStatusText.setText('Unknown')
            self.gameStatusText.setColour(colours.inactive)

        self.blueTeamName, self.redTeamName = cmd.getTeamNames()
        self.gameMode = cmd.getGameMode()
        if not self.inputsEdited:
            self.populateInputs()

    def draw(self, screen):
        t = timeNow()
        if t > self._lastStatusUpdate + 0.5:
            self._lastStatusUpdate = t
            self.updateStatus()

        super(ServerAlreadyExistsMenu, self).draw(screen)

class ShutdownDialog(DialogBox):
    '''Defines the elements and layout thereof of the server shutdown
    confirmation dialog box.'''

    def __init__(self, app):
        super(ShutdownDialog, self).__init__(app, ScaledSize(450, 340),
                'Server Shutdown')
        colours = app.theme.colours

        # Warning message
        text = [
            TextElement(app, 'Are you sure you want',
                    app.screenManager.fonts.mediumMenuFont,
                    Location(DialogBoxAttachedPoint(self, ScaledSize(0, 10),
                    'midtop'), 'midtop'), colours.invalidDataColour),
            TextElement(app, 'to shutdown the server?',
                    app.screenManager.fonts.mediumMenuFont,
                    Location(DialogBoxAttachedPoint(self, ScaledSize(0, 55),
                    'midtop'), 'midtop'), colours.invalidDataColour),
            TextElement(app, 'Doing so will immediately',
                    app.screenManager.fonts.mediumMenuFont,
                    Location(DialogBoxAttachedPoint(self, ScaledSize(0,130),
                    'midtop'), 'midtop'), colours.invalidDataColour),
            TextElement(app, 'end the game and',
                    app.screenManager.fonts.mediumMenuFont,
                    Location(DialogBoxAttachedPoint(self, ScaledSize(0,175),
                    'midtop'), 'midtop'), colours.invalidDataColour),
            TextElement(app, 'disconnect all users!',
                    app.screenManager.fonts.mediumMenuFont,
                    Location(DialogBoxAttachedPoint(self, ScaledSize(0,220),
                    'midtop'), 'midtop'), colours.invalidDataColour)]

        font = app.screenManager.fonts.dialogButtonFont

        # OK Button
        okButton = TextButton(app,  Location(DialogBoxAttachedPoint(self,
                ScaledSize(-100,280), 'midtop'), 'midtop'), 'Confirm', font,
                colours.dialogButtonColour, colours.radioMouseover)
        okButton.onClick.addListener(lambda sender: self.ok())

        # Cancel Button
        cancelButton = TextButton(app,  Location(DialogBoxAttachedPoint(self,
                ScaledSize(100,280), 'midtop'), 'midtop'), 'Cancel', font,
                colours.dialogButtonColour, colours.radioMouseover)
        cancelButton.onClick.addListener(lambda sender: self.cancel())

        # Add elements to screen
        self.elements = text + [okButton, cancelButton]
        self.setColours(colours.redTeam, colours.dialogBoxTextColour,
                colours.dialogBoxTextColour)

    def ok(self):
        self.result = DialogResult.OK
        self.close()

    def cancel(self):
        self.result = DialogResult.Cancel
        self.close()

