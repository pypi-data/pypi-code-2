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
"""Helper functions for acg.

Functions:
load_image -- create a pygame surface from a file

"""

import pygame
from pygame.locals import *

def load_image(filename):
    """Loads pygame surface from file.

    Keyword arguments:
    filename -- path to file to be loaded
    Returns:
    image -- pygame surface

    """
    image = pygame.image.load(filename)
    # Preserve alpha only if the image has an alpha channel.
    if image.get_alpha is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image
