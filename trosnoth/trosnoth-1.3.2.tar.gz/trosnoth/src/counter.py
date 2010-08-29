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
from twisted.internet import task
from twisted.internet.error import CannotListenError
from trosnoth.src.gui.framework import framework, elements
from trosnoth.src.gui import app

from trosnoth.src.network.netman import NetworkManager
from trosnoth.src.network.trosnothdiscoverer import TrosnothDiscoverer
from trosnoth.src.gui.fonts.font import Font

class Interface(framework.CompoundElement):
    def __init__(self, app):
        self.app = app
        self.elements = [
            elements.TextElement(app, ' 0', Font('FreeSans.ttf', 24), (0, 0),
                (255, 255, 255), backColour=(0,0,0))
        ]

class App(app.Application):
    def __init__(self, *args):
        app.Application.__init__(self, *args)

        try:
            self.netman = NetworkManager(6789, 6789)
        except CannotListenError:
            self.netman = NetworkManager(0, None)
        self.discoverer = TrosnothDiscoverer(self.netman)

        self.loop = task.LoopingCall(self.doTick)
        self.loop.start(5)

    def doTick(self, i=[0]):
        self.discoverer.getGames().addCallback(self.gotGames)

    def gotGames(self, games):
        if games is None:
            text = ' ?  '
        else:
            text = ' %s  ' % (len(games),)
        self.interface.elements[0].setText(text)
        
    def stopping(self):
        if self.loop.running:
            self.loop.stop()
        self.discoverer.kill()
        app.Application.stopping(self)

def main():
    app = App((100, 60), 0, 'Trosnoth Counter', Interface)
    app.run_twisted()

if __name__ == '__main__':
    main()
