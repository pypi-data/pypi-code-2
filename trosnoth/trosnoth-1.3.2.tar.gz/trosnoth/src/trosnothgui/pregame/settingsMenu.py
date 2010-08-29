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

from trosnoth.src.trosnothgui.pregame.displaySettingsTab import DisplaySettingsTab
from trosnoth.src.trosnothgui.pregame.keymapTab import KeymapTab
from trosnoth.src.trosnothgui.pregame.soundSettingsTab import SoundSettingsTab
from trosnoth.src.trosnothgui.pregame.themeTab import ThemeTab
from trosnoth.src.gui.framework import framework, elements
from trosnoth.src.gui.framework.tabContainer import TabContainer, TabSize
from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui import defines
from trosnoth.src.utils.event import Event


class SettingsMenu(framework.CompoundElement):
    def __init__(self, app, onClose=None, onRestart=None,
            showThemes=True):
        super(SettingsMenu, self).__init__(app)

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)
        self.onRestart = Event()
        if onRestart is not None:
            self.onRestart.addListener(onRestart)

        area = ScaledArea(50,140,924, 570)
        bg = pygame.Surface((924, 500))
        bg.fill((0,40,0))
        if defines.useAlpha:
            bg.set_alpha(192)
        font = app.screenManager.fonts.bigMenuFont
        self.tabContainer = TabContainer(self.app, area, font,
                app.theme.colours.tabContainerColour)
        bp = elements.SizedPicture(app, bg, Location(AttachedPoint((0,0),
                self.tabContainer._getTabRect)), TabSize(self.tabContainer))

        displayTab = DisplaySettingsTab(app, onClose=self.onClose.execute)
        self.tabContainer.addTab(displayTab)
        
        keymapTab = KeymapTab(app, onClose=self.onClose.execute)
        self.tabContainer.addTab(keymapTab)

        soundTab = SoundSettingsTab(app, onClose=self.onClose.execute)
        self.tabContainer.addTab(soundTab)

        if showThemes:
            themeTab = ThemeTab(app, onClose=self.onClose.execute,
                    onRestart=self.onRestart.execute)
            self.tabContainer.addTab(themeTab)
        
        self.elements = [bp, self.tabContainer]
