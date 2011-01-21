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
import random

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


class BadGuy(pygame.sprite.Sprite):

    """The bad guy."""

    def __init__(self, data):
        """Initialize BadGuy."""
        pygame.sprite.Sprite.__init__(self)
        self.guy = random.choice(['advisor', 'bondguy', 'fireman', 'policeman',
                                  'schoolboard', 'transitadvisor'])
        self.image = acg.tools.load_image(os.path.join(data['images'],
                                                       self.guy + '.png'))
        self.rect = self.image.get_rect()
        self.side = random.randint(0, 1)
        if self.side == 0:
            self.rect.topleft = (-63, random.randint(0, 401))
            if self.guy == 'bondguy' or self.guy == 'fireman' or \
               self.guy == 'schoolboard' or self.guy == 'advisor':
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.rect.topleft = (863, random.randint(0, 401))
            if self.guy == 'transitadvisor' or self.guy == 'policeman':
                self.image = pygame.transform.flip(self.image, True, False)
        self.speed = random.randint(1, 4) / 10

    def update(self, time):
        """Update position of BadGuy, he runs straight across.
        
        Keyword Arguments:
        time -- milliseconds since last update

        """
        if self.side == 0:
            self.rect[0] += self.speed * time
            if self.rect[0] > 800:
                self.kill()
        else:
            self.rect[0] -= self.speed * time
            if self.rect[0] < -63:
                self.kill()


class PopUp(pygame.sprite.Sprite):
    
    """A bad guy that pops up from the bottom of the screen."""

    def __init__(self, data):
        """Initialize the PopUp."""
        pygame.sprite.Sprite.__init__(self)
        self.guy = 'billnye' if random.randint(0, 255) == 0 else 'healthlady'
        if self.guy == 'billnye':
            self.frames = [acg.tools.load_image(os.path.join(data['images'],
                           'billnye', 'nye{0}.png'.format(i)))
                           for i in range(7)]
            self.counter = 0
            self.frame = 0
            self.image = self.frames[self.frame]
            self.speed = 0.3
        else:
            self.image = acg.tools.load_image(os.path.join(data['images'],
                                                           'healthlady.png'))
            self.speed = random.randint(1, 3) / 10
        self.rect = self.image.get_rect()
        self.rect.topleft = (random.randint(0, 737), 559)

    def update(self, time):
        """Update position of PopUp, they go straight up."""
        if self.guy == 'billnye':
            self.counter += time
            if self.counter > 80:
                self.frame += 1
                if self.frame > 6:
                    self.frame = 0
                self.counter -= 80 * self.counter // 80
            self.image = self.frames[self.frame]
        self.rect[1] -= self.speed * time
        if self.rect[1] < -79:
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
