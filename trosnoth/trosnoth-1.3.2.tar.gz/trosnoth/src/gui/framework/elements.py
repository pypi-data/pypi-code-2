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

import pygame
import pygame.locals as pgl
from trosnoth.src.gui.common import *
from trosnoth.src.utils.event import Event
from trosnoth.src.gui import colours

from framework import *

class PictureElement(Element):
    '''Displays a picture at a specified screen location.

    @param  pos         should be an instance of trosnoth.ui.common.Location
    '''
    def __init__(self, app, image, pos=None):
        super(PictureElement, self).__init__(app)
        self.setImage(image)
        if pos is None:
            pos = Location(FullScreenAttachedPoint((0,0), 'center'), 'center')
        self.pos = pos

    def setImage(self, image):
        self.image = image

    def setPos(self, pos):
        self.pos = pos

    def draw(self, screen):
        if hasattr(self.image, 'getImage'):
            surface = self.image.getImage(self.app)
        else:
            surface = self.image

        rect = pygame.Rect(surface.get_rect())
        if hasattr(self.pos, 'apply'):
            self.pos.apply(self.app, rect)
        else:
            pos = self.pos
            setattr(rect, defaultAnchor, pos)

        screen.blit(surface, rect.topleft)

class SizedPicture(PictureElement):
    '''
    Display a picture scaled to the specified position.
    @param  pos         should be an instance of trosnoth.ui.common.Location
    '''
    def __init__(self, app, surface, pos, size):
        image = SizedImage(surface, size)
        super(SizedPicture, self).__init__(app, image, pos)

# Convenience wrapper
class Backdrop(PictureElement):
    '''Display a picture scaled to the biggest 4:3 image that will fit in
    the window, with black filling the rest of the window.'''
    def __init__(self, app, name):
        image = SizedImage(name, ScaledScreenSize(), False)
        super(Backdrop, self).__init__(app, image)

    def draw(self, screen):
        screen.fill(colours.backgroundFiller)
        super(Backdrop, self).draw(screen)


class TextElement(Element):
    '''Shows text at a specified screen location.
    @param pos: should be an instance of trosnoth.ui.common.Location'''

    def __init__(self, app, text, font, pos, colour=(0,128,0),
            anchor='topleft', shadow = False, backColour=None):
        super(TextElement, self).__init__(app)

        self.pos = pos
        self.anchor = anchor
        self.image = TextImage(text, font, colour, backColour)
        self.__shadow = None
        self.setShadow(shadow)
        self._surface = None
        self._screenSize = None

    def _getImage(self):
        if (self._surface is None or self._screenSize !=
                self.app.screenManager.size):
            self._surface = self.image.getImage(self.app)
            self._screenSize = self.app.screenManager.size
        return self._surface

    def _getRect(self):
        rect = self._getImage().get_rect()
        pos = self.pos
        if hasattr(pos, 'apply'):
            pos.apply(self.app, rect)
        else:
            setattr(rect, defaultAnchor, pos)

        return rect

    def getText(self):
        return self.image.text

    def setColour(self, colour):
        self.image.colour = colour

    def setText(self, text):
        if self.image.text != text:
            self._surface = None
            self.image.text = text
            if self.__shadow is not None:
                self.__shadow.setText(text)

    def setFont(self, font):
        if self.image.font != font:
            self.image.font = font
            if self.__shadow is not None:
                self.__shadow.setFont(font)
            self._surface = None

    def setPos(self, pos):
        if self.pos != pos:
            self.pos = pos
            if self.__shadow is not None:
                self.__shadow.setPos(self.__getShadowPos())
            self._surface = None

    def __getShadowPos(self):
        height = self.image.font.getHeight(self.app)
        x = (height / 45) + 1
        pos = RelativeLocation(self.pos, (x, x))
        return pos

    def setShadow(self, shadow):
        if shadow:
            if self.__shadow is None:
                self.__shadow = TextElement(self.app, self.image.text,
                        self.image.font, self.__getShadowPos(),
                        colours.shadowDefault, self.anchor, False)
                self._surface = None
        else:
            if self.__shadow is not None:
                self.__shadow = None
                self._surface = None

    def setShadowColour(self, colour):
        if self.__shadow is not None:
            self.__shadow.setColour(colour)
            self._surface = None

    def draw(self, screen):
        if self.__shadow is not None:
            assert self.__shadow.__shadow is None
            self.__shadow.draw(screen)

        rect = self._getRect()

        # Adjust text position based on anchor.
        image = self._getImage()

        rectPos = getattr(rect, self.anchor)
        imagePos = getattr(image.get_rect(), self.anchor)
        pos = (rectPos[0]-imagePos[0], rectPos[1]-imagePos[1])

        screen.blit(image, pos)

class HoverButton(Element):
    '''A button which changes image when the mouse hovers over it.
    @param  pos     should be a trosnoth.ui.common.Location instance
    '''
    def __init__(self, app, pos, stdImage, hvrImage, hotkey=None, onClick=None):
        super(HoverButton, self).__init__(app)

        self.stdImage = stdImage
        self.hvrImage = hvrImage
        self.pos = pos
        self.onClick = Event()
        self.hotkey = hotkey

        self.mouseOver = False

        if onClick is not None:
            self.onClick.addListener(onClick)

    def _getSurfaceToBlit(self):
        img = self._getImageToUse()
        if hasattr(img, 'getImage'):
            return img.getImage(self.app)
        else:
            return img

    def _getImageToUse(self):
        if self.mouseOver:
            return self.hvrImage
        else:
            return self.stdImage

    def _getSize(self):
        img = self._getImageToUse()
        if hasattr(img, 'getSize'):
            return img.getSize(self.app)
        else:
            # pygame.surface.Surface
            return img.get_size()

    def _getPt(self):
        if hasattr(self.pos, 'apply'):
            rect = pygame.Rect((0,0), self._getSize())
            self.pos.apply(self.app, rect)
            return rect.topleft
        else:
            return self.pos

    def _getRect(self):
        if hasattr(self.pos, 'apply'):
            rect = pygame.Rect((0,0), self._getSize())
            self.pos.apply(self.app, rect)
            return rect
        return pygame.Rect(self.pos, self._getSize())



    def processEvent(self, event):
        rect = self._getRect()
        # Passive events.
        if event.type == pgl.MOUSEMOTION:
            self.mouseOver = rect.collidepoint(event.pos)

        # Active events.
        if event.type == pgl.MOUSEBUTTONDOWN and event.button == 1 and \
           rect.collidepoint(event.pos):
            self.onClick.execute(self)
        elif event.type == pgl.KEYDOWN and event.key == self.hotkey:
            self.onClick.execute(self)
        else:
            return event
        return None

    def draw(self, screen):
        # Draw the button.
        screen.blit(self._getSurfaceToBlit(), self._getPt())

class TextButton(HoverButton):
    'A HoverButton which has text rather than images.'
    def __init__(self, app, pos, text, font, stdColour, hvrColour,
                 hotkey=None, backColour=None, onClick=None):
        self.stdImage = TextImage(text, font, stdColour, backColour)
        self.hvrImage = TextImage(text, font, hvrColour, backColour)

        super(TextButton, self).__init__(app, pos, self.stdImage, self.hvrImage, hotkey, onClick)

    def setText(self, text):
        self.stdImage.text = text
        self.hvrImage.text = text
