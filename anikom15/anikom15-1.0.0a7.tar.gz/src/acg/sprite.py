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
"""All sprite classes."""

import os

import pygame
from pygame.locals import *

import acg

class Bullet(pygame.sprite.Sprite):

    """A bullet, fired by TaxMan but can be fired from anything."""

    def __init__(self, pos, direction, data):
        """Initialize a bullet.
        
        Keyword arguments:
        pos -- topleft pixel position of bullet
        direction -- 0 for left, anything else (i.e. 1) for right

        """
        pygame.sprite.Sprite.__init__(self)
        self.image = acg.tools.load_image(os.path.join(data['images'],
                                                            'bullet.png'))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.direction = direction

    def update(self, time):
        """Update the position of the bullet.

        If it goes out of bounds it dies.

        Keyword arguments:
        time -- milliseconds since last update

        """
        if self.direction == 0:
            self.rect[0] -= time
        else:
            self.rect[0] += time
        if self.rect[0] < -10 or self.rect[0] > 800 or self.rect[1] < -10 or \
           self.rect[1] > 480:
            self.kill()


class TaxMan(pygame.sprite.Sprite):

    """The Tax Man, a.k.a. Anikom15, the main character.

    Also my alter-ego.

    """

    def __init__(self, data):
        """Initialize TaxMan."""
        pygame.sprite.Sprite.__init__(self)
        self.data = data    # Needed to pass to Bullet
        self.image = acg.tools.load_image(os.path.join(data['images'],
                                                            'taxman.png'))
        self.rect = self.image.get_rect()
        self.rect.center = (400, 240)
        self.flipped = False
        self.fired = False
        self.bullet_counter = 0

    def update(self, time):
        """Check key presses and update accordingly.

        Moves the sprite in the direction of pressed arrow keys.
        Creates a bullet sprite if the space bar is pressed and enough
        time has gone by since the last bullet was fired.  Returns the
        bullet sprite if it was created.

        Keyword arguments:
        time -- milliseconds since last update

        """
        sprite = None
        key = pygame.key.get_pressed()
        if key[K_UP]:
            self.rect[1] -= 0.4 * time
        elif key[K_DOWN]:
            self.rect[1] += 0.4 * time
        if key[K_LEFT]:
            self.rect[0] -= 0.3 * time
            if self.flipped:
                self.flipped = False
                self.image = pygame.transform.flip(self.image, True, False)
        elif key[K_RIGHT]:
            self.rect[0] += 0.3 * time
            if not self.flipped:
                self.flipped = True
                self.image = pygame.transform.flip(self.image, True, False)
        if key[K_SPACE]:
            if not self.fired:
                sprite = Bullet(self.rect.center, self.flipped, self.data)
                self.fired = True
        if self.fired:
            self.bullet_counter += time
            if self.bullet_counter > 200:
                self.fired = False
                self.bullet_counter = 0
        # Keep him in bounds
        xlimit = 737
        ylimit = 401
        if self.rect[0] < 0:
            self.rect[0] = 0
        elif self.rect[0] > xlimit:
            self.rect[0] = xlimit
        if self.rect[1] < 0:
            self.rect[1] = 0
        elif self.rect[1] > ylimit:
            self.rect[1] = ylimit
        return sprite
