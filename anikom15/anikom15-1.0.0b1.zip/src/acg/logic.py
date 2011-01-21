# Copyright 2010, 2011 Westley Martinez
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
"""Functions to implement game logic."""

import pygame
from pygame.locals import *

def update(src, dest):
    """Updates the value of src according to dest."""
    if src < dest:
        src += 1
    elif src > dest:
        src -= 1
    return src


def sprite_from_sprite(spritegroup, sprite, time):
    """Takes sprites returned from a sprite and adds it to a group.
    
    sprite is first updated, and if it returns something (i.e. a
    sprite) it is added to spritegroup.
    
    """
    if sprite.alive():
        newsprite = sprite.update(time)
        if newsprite is not None:
            spritegroup.add(newsprite)


def update_collisions(players, killers, enemies):
    """Checks for collisions among three sprite groups.

    players is the sprite group for playable sprites
    killers is the sprite group to represent weaponry of players
    enemies is the sprite group for enemies who kill players

    """
    values = []
    spritedict = pygame.sprite.groupcollide(killers, enemies, True, True)
    for spritelist in spritedict:
        for sprite in spritedict[spritelist]:
            if sprite.guy == 'billnye':
                value = 10
                color = (85, 85, 255)
            elif sprite.guy == 'transitadvisor':
                    value = 5
                    color = (85, 255, 85)
            elif sprite.guy == 'advisor':
                if sprite.speed == 0.1:
                    value = -4
                elif sprite.speed == 0.2:
                    value = -3
                elif sprite.speed == 0.3:
                    value = -2
                else:
                    value = -1
                color = (255, 85, 85)
            else:
                value = sprite.speed * 10
                color = (85, 255, 85)
            values.append((value, color, sprite))
    for player in players:
        if player.alive():
            for sprite in pygame.sprite.spritecollide(player, enemies, False):
                if sprite.guy != 'advisor':
                    player.kill()
    return values
