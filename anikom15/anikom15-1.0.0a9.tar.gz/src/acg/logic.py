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
