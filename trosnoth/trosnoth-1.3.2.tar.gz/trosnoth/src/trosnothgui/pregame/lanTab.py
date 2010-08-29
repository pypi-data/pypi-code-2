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

from trosnoth.src.utils.utils import timeNow
from trosnoth.src.gui.framework.tab import Tab
from trosnoth.src.gui.framework.listbox import ListBox
from trosnoth.src.gui.framework.elements import TextElement, TextButton
from trosnoth.src.network.networkDefines import validServerVersions
from trosnoth.src.gui.common import Area, AttachedPoint, ScaledSize, Location

class LanTab(Tab):
    def __init__(self, app, tabContainer, startupInterface):
        super(LanTab, self).__init__(app, 'Games')
        colours = app.theme.colours
        self.startupInterface = startupInterface
        self.tabContainer = tabContainer

        self.serverRefreshDeferred = None

        self.serverList = ListBox(self.app,
                Area(AttachedPoint(ScaledSize(20, 60),
                    self.tabContainer._getTabRect), ScaledSize(600,390)),
                [],
                self.app.screenManager.fonts.serverListFont,
                colours.listboxButtons)
        # List of server addresses.
        self._servers = []
        self._lastUpdate = timeNow()

        self.noGamesText = TextElement(self.app, 'no games available',
                self.app.screenManager.fonts.serverListFont,
                Location(AttachedPoint(ScaledSize(20,60),
                   self.tabContainer._getTabRect)),
                colours.noGamesColour
            )
        self.elements = [
            self.button('connect', self.connect, ScaledSize(-50, 50),
                    'topright'),
            self.serverList,
            TextElement(self.app, 'please select a game:',
                self.app.screenManager.fonts.ampleMenuFont, Location(
                AttachedPoint(ScaledSize(20,5),self.tabContainer._getTabRect)),
                colours.listboxTitle),
        ]
        
    def button(self, text, onClick, pos, anchor='topleft'):
        pos = Location(AttachedPoint(pos,self.tabContainer._getTabRect, anchor),
                anchor)
        result = TextButton(self.app, pos, text, self.startupInterface.font,
                self.app.theme.colours.mainMenuColour,
                self.app.theme.colours.white)
        result.onClick.addListener(lambda sender: onClick())
        return result

    def connect(self):
        'Connect button was clicked.'
        # Try to connect.
        if self.serverList.index != -1:
            self.startupInterface.inetConnect(
                    *self._servers[self.serverList.index])

    def refreshServerList(self):
        if self.serverRefreshDeferred is not None:
            return

        # Ask the discovery protocol for a list of servers.
        self.serverRefreshDeferred = self.app.discoverer.getGames()
        self.serverRefreshDeferred.addCallbacks(self.gotServerList,
                self.serverListError)

    def serverListError(self, failure):
        print 'Error getting server list: %s' % (failure,)
        self.gotServerList([])

    def gotServerList(self, results):
        self.serverRefreshDeferred = None
        if results is None:
            print 'Error getting server list'
            results = []

        # Show or hide the "no games" text as appropriate.
        if len(results) == 0:
            if self.noGamesText not in self.elements:
                self.elements.append(self.noGamesText)

            # Update list.
            self.serverList.setItems([])
            self._servers = []
            return

        if self.noGamesText in self.elements:
            self.elements.remove(self.noGamesText)

        # Sort by game name.
        results.sort(lambda i,j: cmp(i[1], j[1]))

        # Update the list.
        items = []
        self._servers = []
        for address, info, location in results:
            if info['version'] not in validServerVersions:
                continue
            items.append('%s (%s:%s)' % (info['name'], location, address[0]))
            self._servers.append(address)

        self.serverList.setItems(items)
        if self.serverList.getIndex() == -1:
            self.serverList.setIndex(0)
        
    def draw(self, screen):
        # Automatically update every half second, but only lazily in case it's
        # not visible.
        time = timeNow()
        if self._lastUpdate < time - 0.5:
            self.refreshServerList()
            self._lastUpdate = time
        
        super(LanTab, self).draw(screen)

