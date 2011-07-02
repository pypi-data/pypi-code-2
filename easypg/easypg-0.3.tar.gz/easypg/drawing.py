# Copyright (c) 2007-2011 Nick Efford <nick.efford (at) gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


"""Tools for drawing text, images and shapes in Pygame."""


__author__  = 'Nick Efford'
__version__ = '0.3'


import os, pygame


class FontManager:
    """A manager for Pygame fonts.
    
       It maintains a 'current font' and caches previously-loaded fonts."""

    DEFAULT_FONT_SIZE = 24

    def __init__(self):
        self.cache = {}
        self._current = None

    @property
    def current(self):
        if not self._current:
            self.set_font(self.DEFAULT_FONT_SIZE)
        return self._current

    def set_font(self, size, name=None, bold=False, italic=False):
        """Sets the current Pygame font.

           If 'name' is a filename, the font will be loaded from that file
           if necessary; otherwise, 'name' is assumed to be the name of
           a system font.  If no value is given for 'name', Pygame's default
           font will be loaded.
           
           Loaded fonts are cached, so switching back to a previously-used
           font is efficient."""

        b = 'b' if bold else ''
        i = 'i' if italic else ''
        key = '{}:{:d}{}{}'.format(name, size, b, i)

        if key in self.cache:
            self._current = self.cache[key]
        elif name == None or os.path.isfile(name):
            font = pygame.font.Font(name, size)
            if bold: font.set_bold(True)
            if italic: font.set_italic(True)
            self._current = self.cache[key] = font
        else:
            font = pygame.font.SysFont(name, size, bold, italic)
            self._current = self.cache[key] = font


fonts = FontManager()   # global font manager


def draw_text(surface, string, colour, position):
    """Draws some anti-aliased text at the given location on the
       specified surface, using the current font and given colour."""

    text = fonts.current.render(string, True, colour)
    surface.blit(text, position)


def draw_image(surface, filename, position=(0, 0), alpha=False):
    """Draws an image loaded from the given filename at the given
       location on the specified surface.  A value of True should be
       given for alpha if the image contains transparent pixels."""

    image = pygame.image.load(filename)
    if alpha:
        surface.blit(image.convert_alpha(), position)
    else:
        surface.blit(image.convert(), position)


def draw_line(surf, col, start, end, width=1, antialias=False, blend=True):
    """Draws a straight line segment of a given colour between two
       points on a surface."""

    if antialias:
        pygame.draw.aaline(surf, col, start, end, blend)
    else:
        pygame.draw.line(surf, col, start, end, width)


def draw_lines(surf, col, pts, closed=False, width=1, antialias=False, blend=True):
    """Draws a sequence of straight line segments of a given colour
       between the points in the given list.  If 'closed' is True,
       an additional line segment is drawn between the first and list
       points."""

    if antialias:
        pygame.draw.aalines(surf, col, closed, pts, blend)
    else:
        pygame.draw.lines(surf, col, closed, pts, width)


# Aliases for standard Pygame drawing functions

draw_rect = pygame.draw.rect
draw_polygon = pygame.draw.polygon
draw_circle = pygame.draw.circle
draw_ellipse = pygame.draw.ellipse
draw_arc = pygame.draw.arc
