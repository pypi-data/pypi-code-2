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

from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.framework.checkbox import CheckBox
from trosnoth.src.gui.framework.tab import Tab
import trosnoth.src.gui.framework.prompt as prompt
from trosnoth.src.trosnothgui.pregame.common import button
from trosnoth.src.trosnothgui import defines
from trosnoth.src.gui.common import ScaledLocation, ScaledArea
from trosnoth.src.utils.event import Event

class DisplaySettingsTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, onClose=None):
        super(DisplaySettingsTab, self).__init__(app, 'Display')

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        font = self.app.screenManager.fonts.bigMenuFont
        smallNoteFont = self.app.screenManager.fonts.smallNoteFont

        colour = self.app.theme.colours.headingColour
        def mkText(text, x, y, textFont=font, anchor='topright'):
            return TextElement(self.app, text, textFont,
                    ScaledLocation(x, y, anchor),
                    colour)

        self.text = [
            mkText('X', 630, 250),
            mkText('Screen Resolution', 400, 250),
            mkText('Fullscreen Mode', 400, 320),
            mkText('Use Alpha Channel', 400, 390),
            mkText('Deselect this option if Ghosts or Phase Shift', 520, 395,
                    smallNoteFont, 'topleft'),
            mkText('cause your framerate to go down.', 520, 425,
                    smallNoteFont, 'topleft'),
            mkText('Smooth Panning', 400, 460),
            mkText('Centre on Player', 400, 530),
        ]

        self.invalidInputText = TextElement(self.app, '', font,
                                            ScaledLocation(512, 185,'midtop'),
                                            (192, 0,0))

        self.widthInput = prompt.InputBox(self.app, ScaledArea(450, 240, 150, 60),
                                          initValue = str(self.app.screenManager.size[0]),
                                          font = font,
                                          maxLength = 4,
                                          validator = prompt.intValidator)

        self.widthInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.widthInput.onClick.addListener(self.setFocus)
        self.widthInput.onTab.addListener(self.tabNext)

        self.heightInput = prompt.InputBox(self.app, ScaledArea(642, 240, 150, 60),
                                          initValue = str(self.app.screenManager.size[1]),
                                          font = font,
                                          maxLength = 4,
                                          validator = prompt.intValidator)

        self.heightInput.onEnter.addListener(lambda sender: self.saveSettings())
        self.heightInput.onClick.addListener(self.setFocus)
        self.heightInput.onTab.addListener(self.tabNext)

        self.tabOrder = [self.widthInput, self.heightInput]
        
        self.fullscreenBox = CheckBox(self.app, ScaledLocation(450, 330),
                                             text = '',
                                             font = font,
                                             colour = (192,192,192),
                                             initValue = self.app.screenManager.isFullScreen())
        self.fullscreenBox.onValueChanged.addListener(self.fullscreenChanged)

        self.alphaBox = CheckBox(self.app, ScaledLocation(450, 400),
                                 text = '',
                                 font = font,
                                 colour = (192,192,192),
                                 initValue = defines.useAlpha)
        
        self.panningBox = CheckBox(self.app, ScaledLocation(450, 470),
                                 text = '',
                                 font = font,
                                 colour = (192,192,192),
                                 initValue = app.displaySettings.smoothPanning)
        
        self.centreOnPlayerBox = CheckBox(self.app, ScaledLocation(450, 530),
                                 text = '',
                                 font = font,
                                 colour = (192,192,192),
                                 initValue = app.displaySettings.centreOnPlayer)

        self.input = [self.widthInput, self.heightInput, self.widthInput,
                self.fullscreenBox, self.alphaBox, self.panningBox,
                self.centreOnPlayerBox]
        
        self.elements = self.text + self.input + \
                        [self.invalidInputText,
                         button(app, 'save',
                                self.saveSettings,
                                (-100, -75), 'midbottom'),
                         button(app, 'cancel',
                                self.cancelMenu,
                                (100, -75), 'midbottom'),
                         ]
        self.setFocus(self.widthInput)

        
    def cancelMenu(self):
        self.fullscreenBox.setValue(self.app.screenManager.isFullScreen())
        self.alphaBox.setValue(defines.useAlpha)
        self.panningBox.setValue(self.app.displaySettings.smoothPanning)
        self.centreOnPlayerBox.setValue(self.app.displaySettings.centreOnPlayer)
        self.heightInput.setValue(str(self.app.screenManager.size[1]))
        self.widthInput.setValue(str(self.app.screenManager.size[0]))

        self.onClose.execute()

    def saveSettings(self):
        values = self.getValues()
        if values is not None:
            screenSize, fullScreen, useAlpha, smoothPanning, centreOnPlayer = \
                values

            # Save these values.
            self.app.displaySettings.fullScreen = fullScreen
            self.app.displaySettings.useAlpha = useAlpha
            self.app.displaySettings.smoothPanning = smoothPanning
            self.app.displaySettings.centreOnPlayer = centreOnPlayer
            if fullScreen:
                self.app.displaySettings.fsSize = screenSize
            else:
                self.app.displaySettings.size = screenSize

            # Write to file and apply.
            self.app.displaySettings.save()
            self.app.displaySettings.apply()

            self.onClose.execute()

    def getValues(self):

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value
        useAlpha = self.alphaBox.value
        smoothPanning = self.panningBox.value
        centreOnPlayer = self.centreOnPlayerBox.value

        # The resolutionList is used when fullScreen is true.
        resolutionList = pygame.display.list_modes()
        resolutionList.sort()
        minResolution = resolutionList[0]
        maxResolution = resolutionList[-1]

        if not fullScreen:
            minResolution = (320, 240)

        # These values are used when fullScreen is false.
        # TODO: instead of using the maximum of all possible resolutions,
        # use the current resolution as the maximum size instead
        # (but only when fullScreen == false)
        widthRange = (minResolution[0], maxResolution[0])
        heightRange = (minResolution[1], maxResolution[1])

        if not widthRange[0] <= width <= widthRange[1]:
            self.incorrectInput('Screen width must be between %d and %d' %
                                (widthRange[0], widthRange[1]))
            width = None
            return
        if not heightRange[0] <= height <= heightRange[1]:
            self.incorrectInput('Screen height must be between %d and %d' %
                                (heightRange[0], heightRange[1]))
            height = None
            return
        if fullScreen:
            selectedResolution = (width, height)
            if selectedResolution not in resolutionList:
                self.incorrectInput('Selected resolution is not valid for this display')
                height = width = None
                return

        self.incorrectInput('')

        return (width, height), fullScreen, useAlpha, smoothPanning, centreOnPlayer

    def getInt(self, value):
        if value == '':
            return 0
        return int(value)
        
    def incorrectInput(self, string):
        self.invalidInputText.setText(string)
        self.invalidInputText.setFont(self.app.screenManager.fonts.bigMenuFont)

    def fullscreenChanged(self, element):
        # If the resolution boxes haven't been touched, swap their values to
        # the appropriate resolution for the new mode.

        height = self.getInt(self.heightInput.value)
        width = self.getInt(self.widthInput.value)
        fullScreen = self.fullscreenBox.value

        if fullScreen:
            # Going to full screen mode.
            if (width, height) != self.app.displaySettings.size:
                return
            width, height = self.app.displaySettings.fsSize
        else:
            # Going from full screen mode.
            if (width, height) != self.app.displaySettings.fsSize:
                return
            width, height = self.app.displaySettings.size

        self.heightInput.setValue(str(height))
        self.widthInput.setValue(str(width))
