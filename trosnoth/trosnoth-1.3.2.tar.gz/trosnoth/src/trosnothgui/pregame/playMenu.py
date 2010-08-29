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
from trosnoth.src.gui.framework.elements import SizedPicture, TextButton
from trosnoth.src.gui.framework.tabContainer import TabContainer, TabSize
from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui.pregame.lanTab import LanTab
from trosnoth.src.trosnothgui.pregame.internetTab import InternetTab
from trosnoth.src.trosnothgui.pregame.serverSetupTab import ServerSetupTab
from trosnoth.src.trosnothgui import defines

class PlayMenu(framework.CompoundElement):
    def __init__(self, app, startupInterface):
        super(PlayMenu, self).__init__(app)
        self.startupInterface = startupInterface

        area = ScaledArea(50,140,924, 570)
        bg = pygame.Surface((924, 500))
        bg.fill((32,0,48))
        if defines.useAlpha:
            bg.set_alpha(192)
        
        self.tabContainer = TabContainer(self.app, area, startupInterface.font,
                app.theme.colours.tabContainerColour)
        bp = SizedPicture(app, bg, Location(AttachedPoint((0,0),self.tabContainer._getTabRect)), TabSize(self.tabContainer))
        
        lanTab = LanTab(app, self.tabContainer, startupInterface)
        self.tabContainer.addTab(lanTab)
        
        internetTab = InternetTab(app, self.tabContainer, startupInterface)
        self.tabContainer.addTab(internetTab)
        
        self.startTab = ServerSetupTab(app, self.tabContainer, startupInterface)
        self.tabContainer.addTab(self.startTab)
        
        cancelButton = self.button('cancel',   startupInterface.mainMenu,  (-50,-40), 'bottomright')
        #startupInterface.heading('play'),
        self.elements = [bp, self.tabContainer, cancelButton]
        
    def button(self, text, onClick, pos, anchor='topleft'):
        pos = Location(AttachedPoint(ScaledSize(*pos),self.tabContainer._getTabRect, anchor), anchor)
        result = TextButton(self.app, pos, text, self.startupInterface.font,
                self.app.theme.colours.mainMenuColour,
                self.app.theme.colours.white)
        result.onClick.addListener(lambda sender: onClick())
        return result
    
    def setName(self, name):
        self.startTab.setName(name)

    def regainedFocus(self):
        # Select the LAN tab by default
        self.tabContainer._tabSelected(0)

    def processEvent(self, event):
        if event.type == pygame.locals.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.startupInterface.mainMenu()
        else:
            return super(PlayMenu, self).processEvent(event)        
