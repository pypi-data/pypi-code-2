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

'''defines.py - Used for useful general definitions.'''
import pygame.locals

# TODO: Make a Settings object.
# The name of the game - this is used to name the window.
gameName = 'Trosnoth'
screenSize = 1024, 768
fullScreen = True
useAlpha = True

maxNameLength = 20


# Things which will be imported with: from defines import *
__all__ = ['gameName', 'screenSize', 'useAlpha', 'fullScreen', 'maxNameLength']
