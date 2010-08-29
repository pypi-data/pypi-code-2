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

import os
import pickle
import base64
import time
import re

from trosnoth.src.utils.jsonImport import json
from trosnoth.src.utils import browser

import trosnoth.src.trosnothgui.defines as defines
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.framework.listbox import ListBox
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.gui.framework.dialogbox import DialogBox, DialogResult, DialogBoxAttachedPoint
from trosnoth.src.gui.common import *
from trosnoth.src.gamerecording.gamerecorder import RecordedGame, RecordedGameException, gameDir, gameExt, recordedGameVersion

from trosnoth.data import getPath, user, makeDirs


class SavedGameMenu(framework.CompoundElement):
    def __init__(self, app, startupInterface):
        super(SavedGameMenu, self).__init__(app)
        colours = app.theme.colours
        self.startupInterface = startupInterface

        font = self.app.screenManager.fonts.ampleMenuFont
        smallFont = self.app.screenManager.fonts.bigMenuFont

        # Static text
        self.staticText = [TextElement(self.app, 'server details:', font,
                                       ScaledLocation(985, 130, 'topright'),
                                       colours.headingColour),
                           TextElement(self.app, 'date and time:', font,
                                       ScaledLocation(985, 370, 'topright'),
                                       colours.headingColour),
                           TextElement(self.app, 'replay:', font,
                                       ScaledLocation(670, 535, 'topleft'),
                                       colours.headingColour),
                           TextElement(self.app, 'stats:', font,
                                       ScaledLocation(670, 605, 'topleft'),
                                       colours.headingColour)]

        # Dynamic text
        self.listHeaderText = TextElement(self.app, 'available game files:', font,
                                           ScaledLocation(50, 130),
                                           colours.headingColour)
        self.noFiles1Text = TextElement(self.app, '', font,
                                       ScaledLocation(50, 200),
                                       colours.noGamesColour)
        self.noFiles2Text = TextElement(self.app, '', font,
                                       ScaledLocation(50, 250),
                                       colours.noGamesColour)
        self.serverNameText = TextElement(self.app, '', smallFont,
                                          ScaledLocation(985, 185, 'topright'),
                                          colours.startButton)
        self.serverDetailsText = TextElement(self.app, '', font,
                                             ScaledLocation(985, 240, 'topright'),
                                             colours.startButton)
        self.teamNamesText = TextElement(self.app, '', smallFont,
                                         ScaledLocation(985, 295, 'topright'),
                                         colours.startButton)
        self.dateText = TextElement(self.app, '', smallFont,
                                    ScaledLocation(985, 430, 'topright'),
                                    colours.startButton)
        self.lengthText = TextElement(self.app, '', smallFont,
                                      ScaledLocation(985, 480, 'topright'),
                                      colours.startButton)
        self.noReplayText = TextElement(self.app, '', smallFont,
                                        ScaledLocation(985, 535, 'topright'),
                                        colours.noGamesColour)
        self.noStatsText = TextElement(self.app, '', smallFont,
                                       ScaledLocation(985, 605, 'topright'),
                                       colours.noGamesColour)

        self.dynamicText = [self.listHeaderText, self.noFiles1Text, self.noFiles2Text, self.serverNameText,
                            self.serverDetailsText, self.teamNamesText, self.dateText, self.lengthText,
                            self.noReplayText, self.noStatsText]

        # Text buttons
        self.watchButton = TextButton(self.app, ScaledLocation(985, 535, 'topright'),
                                      '', font,
                                      colours.mainMenuColour, colours.white)
        self.watchButton.onClick.addListener(lambda sender: self.watchReplay())

        self.statsButton = TextButton(self.app, ScaledLocation(985, 605, 'topright'),
                                      '', font,
                                      colours.mainMenuColour, colours.white)
        self.statsButton.onClick.addListener(lambda sender: self.viewStats())
        
        self.refreshButton = TextButton(self.app, ScaledLocation(670, 675, 'topleft'),
                                        'refresh', font,
                                        colours.mainMenuColour, colours.white)
        self.refreshButton.onClick.addListener(lambda sender: self.populateList())
        
        self.cancelButton = TextButton(self.app, ScaledLocation(985, 675, 'topright'),
                                       'cancel', font,
                                       colours.mainMenuColour, colours.white)
        self.cancelButton.onClick.addListener(lambda sender: self.startupInterface.mainMenu())

        self.buttons = [self.watchButton, self.statsButton, self.refreshButton, self.cancelButton]

        # Replay list
        self.gameList = ListBox(self.app, ScaledArea(50, 200, 550, 550),
                                  [], smallFont, colours.listboxButtons)
        self.gameList.onValueChanged.addListener(self.updateSidebar)

        # Combine the elements        
        self.elementsFiles = self.staticText + self.dynamicText + self.buttons + [self.gameList]
        self.elementsNoFiles = self.dynamicText + self.buttons

        # Populate the list of replays
        self.populateList()

    def populateList(self):

        # Clear out the sidebar
        self.serverNameText.setText('')
        self.serverDetailsText.setText('')
        self.teamNamesText.setText('')
        self.dateText.setText('')
        self.lengthText.setText('')
        self.watchButton.setText('')
        self.statsButton.setText('')
        self.noFiles1Text.setText('')
        self.noFiles2Text.setText('')
        self.noReplayText.setText('')
        self.noStatsText.setText('')
        self.listHeaderText.setText('available game files:')
        self.gameList.index = -1
        self.elements = self.elementsFiles[:]
        if json == None:
            self.noFiles1Text.setText('Please install json')
            self.noFiles2Text.setText('to view statistics')
            return
        # Get a list of files with the name '*.tros'
        logDir = getPath(user, gameDir)
        makeDirs(logDir)
        fileList = []

        for fname in os.listdir(logDir):
            if os.path.splitext(fname)[1] == gameExt:
                fileList.append(fname)

        # Assume all files are valid for now
        validFiles = fileList[:]

        self.gameInfo = {}
        oldFound = False

        for fname in fileList:
            try:
                game = RecordedGame(os.path.join(logDir, fname))
            except RecordedGameException:
                validFiles.remove(fname)
                continue
            except:
                print 'invalid file: %s' % (fname,)
                continue
            else:
                if game.recordedGameVersion != recordedGameVersion:
                    validFiles.remove(fname)
                    oldFound = True

            self.gameInfo[os.path.splitext(fname)[0]] = game

        # Sort the games with most recent first.
        items = [(v.unixTimestamp, n) for n, v in self.gameInfo.iteritems()]
        items.sort(reverse=True)
        items = [n for v,n in items]
        self.gameList.setItems(items)

        if len(self.gameInfo) == 0:
            self.elements = self.elementsNoFiles[:]
            self.listHeaderText.setText('0 available game files:')
            if oldFound:
                self.noFiles1Text.setText('Some games were found from')
                self.noFiles2Text.setText('previous Trosnoth versions')
            else:                
                self.noFiles1Text.setText('You have not yet run any')
                self.noFiles2Text.setText('games on this computer')
        else:
            self.gameList.setIndex(0)
            self.updateSidebar(0)
            if len(self.gameInfo) == 1:
                self.listHeaderText.setText('1 available game file:')
            else:
                self.listHeaderText.setText('%d available game files:' % len(self.gameInfo))
            
    def updateSidebar(self, listID):
        # Update the details on the sidebar
        displayName = self.gameList.getItem(listID)

        # Server title
        self.serverNameText.setText(self.gameInfo[displayName].alias)

        # Map size
        self.serverDetailsText.setText('Map size: %d x %d' % (self.gameInfo[displayName].halfMapWidth,
                                                              self.gameInfo[displayName].mapHeight))

        # Team names
        blueTeam = self.gameInfo[displayName].teamAname
        redTeam = self.gameInfo[displayName].teamBname
        self.teamNamesText.setText(blueTeam + ' vs ' + redTeam)

        # Date and time of match
        datePython = map(int, self.gameInfo[displayName].dateTime.split(','))
        dateString = time.strftime('%a %d/%m/%y, %H:%M', datePython)
        self.dateText.setText(dateString)

        # Length of match
        dateUnix = time.mktime(datePython)
        if self.gameInfo[displayName].wasFinished():
            lastUnix = self.gameInfo[displayName].gameFinishedTimestamp

            lengthSeconds = int(lastUnix - dateUnix)
            lengthMinutes, lengthSeconds = divmod(lengthSeconds, 60)

            secPlural = ('s', '')[lengthSeconds == 1]
            minPlural = ('s', '')[lengthMinutes == 1]
            if lengthMinutes == 0:
                lengthString = '%d second%s' % (lengthSeconds,secPlural)
            else:
                lengthString = '%d min%s, %d sec%s' % (lengthMinutes, minPlural, lengthSeconds, secPlural)

            self.lengthText.setText(lengthString)
        
        # Enable the replay button
        if self.gameInfo[displayName].replayFilename is not None and \
           os.path.exists(self.gameInfo[displayName].replayFilename):
            self.watchButton.setText('watch')
            self.noReplayText.setText('')
        else:
            self.watchButton.setText('')
            self.noReplayText.setText('unavailable')

        # Enabled the stats button
        if self.gameInfo[displayName].statsFilename is not None and \
           os.path.exists(self.gameInfo[displayName].statsFilename):
            self.statsButton.setText('view')
            self.noStatsText.setText('')
        else:
            self.statsButton.setText('')
            self.noStatsText.setText('unavailable')

    def watchReplay(self):
        '''Watch replay button was clicked.'''
        # Try to create a replay server.
        #if self.gameList.index != -1:
        self.startupInterface.replayConnect(self.gameInfo[self.gameList.getItem()].replayFilename)

    def viewStats(self, allGames = False):
        '''View stats button was clicked.'''
        game = self.gameInfo[self.gameList.getItem()]
##        try:
        self.htmlPath = game.generateHtmlFile()
##        except:
##            print 'Unable to generate statistics for %s' % (game.filename)
##        else:
        self.statsGeneratedBox = StatsGeneratedDialog(self.app)
        self.statsGeneratedBox.onClose.addListener(self._dialogClosed)
        self.statsGeneratedBox.Show()

    def _dialogClosed(self):
        if self.statsGeneratedBox.result == DialogResult.OK:
            browser.openPage(self.app, self.htmlPath)

    def draw(self, surface):
        super(SavedGameMenu, self).draw(surface)
        colours = self.app.theme.colours
        width = max(int(3*self.app.screenManager.scaleFactor), 1)
        scalePoint = self.app.screenManager.placePoint
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((0,130)), scalePoint((1024, 130)), width)
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,130)), scalePoint((640, 768)), width)
        #pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,364)), scalePoint((1024, 364)), width)
        pygame.draw.line(surface, colours.mainMenuColour, scalePoint((640,540)), scalePoint((1024, 540)), width)

class StatsGeneratedDialog(DialogBox):
    '''Defines the elements and layout thereof of the 'stats successfully generated' dialog box.'''

    def __init__(self, app):
        super(StatsGeneratedDialog, self).__init__(app, ScaledSize(450, 350), 'Statistics File Generated')
        colours = app.theme.colours

        text = ['A HTML file has been',
                'created containing the',
                'requested statistics.',
                'Do you want to',
                'open this file now?']
        textElements = []

        yValue = 10
        for string in text:
            textElements.append(TextElement(app, string, app.screenManager.fonts.mediumMenuFont,
                                Location(DialogBoxAttachedPoint(self, ScaledSize(0, yValue), 'midtop'), 'midtop'),
                                colours.startButton))
            yValue += 45
        
        font = self.app.screenManager.fonts.dialogButtonFont

        # OK Button
        okButton = TextButton(app, Location(DialogBoxAttachedPoint(
                              self, ScaledSize(-100,290), 'midtop'), 'midtop'),
                              'Yes', font, colours.mainMenuColour, colours.white)
        
        okButton.onClick.addListener(lambda sender: self.ok())

        # Cancel Button
        cancelButton = TextButton(app, Location(DialogBoxAttachedPoint(
                                  self, ScaledSize(100,290), 'midtop'), 'midtop'),
                                  'No', font, colours.mainMenuColour, colours.white)
        
        cancelButton.onClick.addListener(lambda sender: self.cancel())

        # Add elements to screen
        self.elements = textElements + [okButton, cancelButton]
        self.setColours(None, None, colours.black)

    def ok(self):
        self.result = DialogResult.OK
        self.Close()
        
    def cancel(self):
        self.result = DialogResult.Cancel
        self.Close()
