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

from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework import prompt
from trosnoth.gui.framework.elements import TextElement, TextButton
from trosnoth.gui.framework import framework
from trosnoth.gui.common import (ScaledArea, ScaledLocation, Location,
        ScaledSize, AttachedPoint)
from trosnoth.utils.unrepr import unrepr
from trosnoth.network.networkDefines import defaultServerPort
from trosnoth.data import getPath, user
from trosnoth.utils.event import Event

log = logging.getLogger('internetTab')

class InternetTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, tabContainer, onInetConnect):
        super(InternetTab, self).__init__(app, 'IP Connect')
        self.onInetConnect = Event(onInetConnect)
        self.tabContainer = tabContainer

        self.font = font = self.app.screenManager.fonts.bigMenuFont
        self.serverNameBox = prompt.InputBox(self.app, ScaledArea(352, 300,
                442, 60), font=font)
        self.serverNameBox.onClick.addListener(self.setFocus)
        self.serverNameBox.onTab.addListener(self.tabNext)
        self.serverNameBox.onEnter.addListener(self.tabNext)

        self.portBox = prompt.InputBox( self.app, ScaledArea(352, 450, 442, 60),
                font=font, validator = prompt.intValidator)
        self.portBox.onClick.addListener(self.setFocus)
        self.portBox.onTab.addListener(self.tabNext)
        self.portBox.onEnter.addListener(lambda sender: self.connect())

        self.tabOrder = [self.serverNameBox, self.portBox]

        colours = app.theme.colours
        self.elements = [
            self.serverNameBox,
            self.portBox,
            self.button('connect',  self.connect, (0, -40), 'midbottom'),
            self.button('clear',  self.clear, (-50, 140), 'topright'),
            TextElement(self.app, 'Server / IP:', font, ScaledLocation(320, 315,
            'topright'), colours.headingColour),
            TextElement(self.app, 'Port:', font, ScaledLocation(320, 465,
                    'topright'), colours.headingColour),
        ]

        # Restore previous internet server, if one exists
        previousServerData = self.restore()
        if previousServerData != None:
            self.serverNameBox.value = str(previousServerData["host"])
            self.portBox.value = str(previousServerData["port"])
        else:
            self.clear()

    def button(self, text, onClick, pos, anchor='topleft'):
        pos = Location(AttachedPoint(ScaledSize(*pos),
                self.tabContainer._getTabRect, anchor), anchor)
        colours = self.app.theme.colours
        result = TextButton(self.app, pos, text, self.font,
                colours.secondMenuColour, colours.white)
        result.onClick.addListener(lambda sender: onClick())
        return result

    def showMenu(self):
        'Called when this menu is shown.'
        self.setFocus(self.serverNameBox)

    def connect(self):
        'Connect button was clicked.'
        # First, save the server hostname and port
        self.save()

        # Try to connect.
        self.onInetConnect.execute(self.serverNameBox.value,
                int(self.portBox.value))

    def clear(self):
        self.serverNameBox.value = ""
        self.portBox.value = self.portBox.value = str(defaultServerPort)
        self.showMenu()

    def activated(self):
        self.showMenu()

    def save(self):
        """
        This saves the server and port so they can be restored when this
        tab is loaded again.
        """
        serversFilename = getPath(user, 'servers')
        try:
            serversFile = open(serversFilename, 'w')
            serversFile.write(repr({'host' : str(self.serverNameBox.value),
                                    'port' : int(self.portBox.value),
                                    }))
            serversFile.close()
        except Exception, e:
            log.exception('While saving inet server: %s', e)

    def restore(self):
        """
        This reads and returns the saved host and port as a dict.
        If the settings file cannot be found/read, it does not return
        anything.
        """
        try:
            serversFilename = getPath(user, 'servers')
            serversFile = open(serversFilename, 'r')
            serversData = serversFile.read()
            serversFile.close()
            return unrepr(serversData)
        except IOError:
            pass
        except Exception, e:
            log.exception('While saving inet server: %s', e)
