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

from trosnoth.src.utils.utils import timeNow, new
from trosnoth.src.gui.common import defaultAnchor, addPositions
from framework import *
import pygame

class Clock(Element):
    '''
    A graphical clock class; could be used to show a countdown or a count-up
    of the game in progress. Counts to the second.
    '''
    
    def __init__(self, app, timer, pos, font,
                 colour = (0,0,0), bgColour = None):
        super(Clock, self).__init__(app)
        self.timer = timer
        self.pos = pos
        self.size = None
        self.colour = colour
        self.bgColour = bgColour
        # Number of seconds counted down/remaining
        self.currentVal = 0
        
        self.font = font

    # Rather than the size of this object changing as the numbers change,
    # set a fixed size.
    # For no fixed size, call with size as None
    def setFixedSize(self, size):
        self.size = size

    # Since 'None' as a bgColour means 'no background', call this function
    # with bgColour = False to set it to None.
    def setColours(self, fontColour = None, bgColour = None):
        if fontColour is not None:
            self.colour = fontColour
        if bgColour is not None:
            if bgColour is False:
                self.bgColour = None
            else:
                self.bgColour = bgColour

    def tick(self, deltaT):
        self.timer.tick(deltaT)

    def _getSize(self):
        if self.size is None:
            return addPositions(self.font.size(self.app, self.timer.getTimeString()), (2,0))
        else:
            return self.size.getSize(self.app)

    def _getRect(self):
        rect = pygame.Rect((0,0), self._getSize())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
        else:
            setattr(rect, defaultAnchor, self.pos)
        return rect

    def _getPt(self):
        return self._getRect().topleft

    def draw(self, surface):
        if self.bgColour is not None:
            clockImage = self.font.render(self.app, self.timer.getTimeString(), True, self.colour, self.bgColour)
            rect = self._getRect()
            surface.fill(self.bgColour, rect)
            clockRect = clockImage.get_rect()
            clockRect.center = rect.center
            surface.blit(clockImage, clockRect.topleft)
        else:
            clockImage = self.font.render(self.app, self.timer.getTimeString(), True, self.colour)
            surface.blit(clockImage, self._getPt())
