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
"""acg __init__.py

Functions:
set_options -- set constants
init -- initialize pygame
shutodwn -- quit pygame

"""

import os

import pygame
from pygame.locals import *

import acg.tools

DATA = {'version': '1.0.0a2'}
SETTINGS = {}
PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(PATH)

def set_options(options):
    """Set constant variables.

    Keyword arguments:
    options -- dictionary of settings

    """
    for key in options:
        SETTINGS[key] = options[key]
    SETTINGS['resolution'] = (800, 480)
    SETTINGS['srcalpha'] = SRCALPHA
    SETTINGS['doublebuf'] = DOUBLEBUF if options['doublebuf'] else 0
    SETTINGS['hwsurface'] = HWSURFACE if options['hwsurface'] or \
                            options['doublebuf'] else 0
    SETTINGS['fullscreen'] = FULLSCREEN if options['fullscreen'] or \
                             options['hwsurface'] or \
                             options['doublebuf'] else 0


def init():
    """Initialize all the stuff needed for the game, display, mixer, &c."""
    pygame.mixer.pre_init(SETTINGS['afrequency'], SETTINGS['asize'],
                          SETTINGS['achannels'], SETTINGS['abuffersize'])
    pygame.init()
    pygame.display.set_caption("Anikom15's Computer Game")
    pygame.mouse.set_visible(False)
    pygame.display.set_mode(SETTINGS['resolution'],
                            SETTINGS['srcalpha'] | SETTINGS['fullscreen'] |
                            SETTINGS['hwsurface'] | SETTINGS['doublebuf'])
    icon = tools.load_image(os.path.join(DIRNAME, 'data', 'images',
                            'icon.png'))
    pygame.display.set_icon(icon)
    if SETTINGS['resolution']:
        pygame.time.wait(3000)


def copyright():
    """Display copyright information."""
    pass


def title():
    """Display the title and allow the user to choose a mode.

    Returns a string that represents the chosen mode.

    """
    return 'quit'


def run(mode):
    """Run the mode selected at the title screen."""
    eval(mode)()


def shutdown():
    """Shutdown all the pygame stuff."""
    pygame.quit()
