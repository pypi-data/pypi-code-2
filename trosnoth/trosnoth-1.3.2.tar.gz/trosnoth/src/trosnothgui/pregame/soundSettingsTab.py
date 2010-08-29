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

from trosnoth.data import getPath, user
from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.gui.framework.checkbox import CheckBox
from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.framework.slider import Slider
import trosnoth.src.gui.framework.prompt as prompt
from trosnoth.src.trosnothgui.pregame.common import button
from trosnoth.src.gui.common import *
from trosnoth.src.utils.event import Event


class SoundSettingsTab(Tab, framework.CompoundElement):
    def __init__(self, app, onClose=None):
        super(SoundSettingsTab, self).__init__(app, "Sounds")

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)

        font = self.app.screenManager.fonts.bigMenuFont
        smallNoteFont = self.app.screenManager.fonts.smallNoteFont
        colours = app.theme.colours

        text = [
            TextElement(self.app, 'Music Volume', font,
                ScaledLocation(400, 280, 'topright'), colours.headingColour),
            TextElement(self.app, 'Enable Music', font,
                ScaledLocation(400, 350, 'topright'), colours.headingColour),
        ]

        initVolume = app.soundSettings.musicVolume
        musicVolumeLabel = TextElement(self.app, '%d' % (initVolume,), font,
                                 ScaledLocation(870, 280, 'topleft'),
                                 colours.headingColour)


        self.musicVolumeSlider = Slider(self.app,
                ScaledArea(450, 280, 400, 40))
        onSlide = lambda volume: musicVolumeLabel.setText("%d" % volume)
        self.musicVolumeSlider.onSlide.addListener(onSlide)
        self.musicVolumeSlider.onValueChanged.addListener(onSlide)
        self.musicVolumeSlider.setVal(initVolume)
        
        self.musicBox = CheckBox(self.app, ScaledLocation(450, 360),
                text = '', font = font, colour = (192,192,192), 
                initValue = app.soundSettings.musicEnabled)

        self.buttons = [
            button(app, 'save', self.saveSettings, (-100, -75), 'midbottom'),
            button(app, 'cancel', self.onClose.execute, (100, -75),
                'midbottom')
        ]
        
        self.elements = text + [musicVolumeLabel, self.musicVolumeSlider,
                self.musicBox] + self.buttons
        
    def saveSettings(self, sender=None):
        playMusic, volume = self.getValues()

        ss = self.app.soundSettings
        ss.musicEnabled = playMusic
        ss.musicVolume = volume

        ss.save()
        ss.apply()

        self.onClose.execute()

    def getValues(self):

        playMusic = self.musicBox.value
        volume = self.musicVolumeSlider.getVal()
        
        return [playMusic, volume]
        
