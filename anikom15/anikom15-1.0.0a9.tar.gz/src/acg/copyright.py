# Copyright 2010 Westley Martinez
#
# This file is part of Anikom15's Computer Game (ACG).
# ACG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ACG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ACG.  If not, see <http://www.gnu.org/licenses/>.
"""Objects for the copyright screen."""

import os

import pygame
from pygame.locals import *

class Copyright():

    """Text to be blitted onto the screen describing the copyright."""

    def __init__(self, font):
        """Initialize Copyright"""
        self.font = font
        self.lines = [font.render('Copyright \u00a9 2010, 2011 Westley \
Mart\u00ednez', True, (255, 255, 255)),
                      font.render('All Rights Reserved.', True,
                                  (255, 255, 255))]
        self.linerects = [self.lines[0].get_rect(centerx=400, centery=240 -
                                                 self.font.get_linesize()),
                          self.lines[1].get_rect(centerx=400, centery=240 -
                                                 self.font.get_linesize() +
                                                 self.font.get_linesize())]
    
    def update(self, screen):
        for line in self.lines:
            screen.blit(line, self.linerects[self.lines.index(line)])
