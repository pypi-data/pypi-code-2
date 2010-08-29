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

from trosnoth.src.gui.framework.menu import MenuDisplay
from trosnoth.src.gui.menu.menu import MenuManager, Menu, MenuItem
from trosnoth.src.model.upgrades import (Turret, Shield, MinimapDisruption,
        PhaseShift, Grenade, Ricochet)
from trosnoth.src.gui.common import Size

class MainMenu(MenuDisplay):
    def __init__(self, app, location, interface, keymapping):
        font = app.screenManager.fonts.ingameMenuFont
        titleColour = (255, 255, 255)
        stdColour = (255, 255, 0)
        hvrColour = (0, 255, 255)
        backColour = (0, 64, 192)
        autosize = True
        hidable = True
        size = Size(175, 10)   # Height doesn't matter when autosize is set.

        self.ACCELERATION = 1000    # pix/s/s

        manager = MenuManager()
        self.buyMenu = buyMenu = Menu(name='Buy Upgrade', listener=interface.doAction, items=[
            MenuItem('Turret (%s)' % Turret.requiredStars, 'turret'),
            MenuItem('Shield (%s)' % Shield.requiredStars, 'shield'),
            MenuItem('Minimap Disruption (%s)' % MinimapDisruption.requiredStars, 'minimap disruption'),
            MenuItem('Phase Shift (%s)' % PhaseShift.requiredStars, 'phase shift'),
            MenuItem('Grenade (%s)' % Grenade.requiredStars, 'grenade'),
            MenuItem('Ricochet (%s)' % Ricochet.requiredStars, 'ricochet'),
            MenuItem('Cancel', 'menu')
        ])
        self.moreMenu = moreMenu = Menu(name='More Actions', listener=interface.doAction, items=[
            MenuItem('Abandon upgrade', 'abandon'),
            MenuItem('Chat', 'chat'),
            MenuItem('Become captain', 'captain'),
            MenuItem('Team is ready', 'team ready'),
            MenuItem('Show/hide HUD', 'toggle interface'),
            MenuItem('Cancel', 'menu')
        ])
        mainMenu = Menu(name='Menu', listener=interface.doAction, items=[
            MenuItem('Respawn', 'respawn'),
            MenuItem('Buy an upgrade...', 'buy upgrade'),
            MenuItem('Settings', 'settings'),
            MenuItem('More...', 'more actions'),
            MenuItem('---'),
            MenuItem('Leave game', 'leave')
        ])

        manager.setDefaultMenu(mainMenu)
        
        super(MainMenu, self).__init__(app, location, size, font, manager,
                                       titleColour, stdColour, hvrColour,
                                       backColour, autosize, hidable,
                                       keymapping)
    def showBuyMenu(self):
        self.manager.reset()
        self.manager.showMenu(self.buyMenu)

    def showMoreMenu(self):
        self.manager.reset()
        self.manager.showMenu(self.moreMenu)

    def escape(self):
        if self.hidden:
            # Just show the existing menu.
            self.hide()
        elif self.manager.menu == self.manager.defaultMenu:
            # Main menu is already selected. Hide it.
            self.hide()
        else:
            # Main menu is not selected. Return to it.
            self.manager.cancel()
