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

from framework import Element, CompoundElement
from elements import TextButton, TextElement
from trosnoth.src.gui.common import translateEvent, Location, AttachedPoint
from trosnoth.src.utils.event import Event
from trosnoth.src.utils.utils import new
import pygame

class ScrollBar(Element):
    defaultWidth = 15
    defaultButtonChange = 20 ## number of pixels moved when button is pressed
    defaultColour = (0,255,0)
    defaultBackColour = (128,128,128)
    def __init__(self, app, parent, pos, horizontal = False):
        super(ScrollBar, self).__init__(app)
        self.width = self.defaultWidth
        self.buttonChange = self.defaultButtonChange
        self.colour = self.defaultColour
        self.backColour = self.defaultBackColour
        self.parent = parent
        self.pos = pos
        self.horizontal = horizontal
        if horizontal:
            self.index = 0
        else:
            self.index = 1

        self.originalPosition = 0
        self.position = 0
        self.beingDraggedFrom = None

    def _getWidth(self):
        return self.width

    # This should be checked before ever being used
    def __checkThisIsValid(self):
        if self.__getDrawableSize() >= self.__getCanvasSize():
            print ("Vertical", "Horizontal")[self.horizontal]
            print "Drawable Area: %d" % (self.__getDrawableSize(),)
            print "Canvas Size: %d" % (self.__getCanvasSize(),)
            assert False, "For there to be a scroll bar, the displaying size must be less than the full size"

    def _getTopLeftPt(self):
        self.__checkThisIsValid()
        return self._getFullRect().topleft

    def _getBarLength(self):
        self.__checkThisIsValid()
        return self.__getDrawableSize() ** 2 / self.__getCanvasSize()

    def _getBarRect(self):
        self.__checkThisIsValid()
        if self.horizontal:
            size = (self._getBarLength(), self._getWidth())
            pos = (self._getTopLeftPt()[0]+self._getPosition(), self._getTopLeftPt()[1])
        else:
            size = (self._getWidth(), self._getBarLength())
            pos = (self._getTopLeftPt()[0], self._getTopLeftPt()[1]+self._getPosition())
        return pygame.rect.Rect(pos, size)

    def __getDrawableSize(self):
        return self.parent._getDrawableSize()[self.index]

    def __getCanvasSize(self):
        return self.parent._getCanvasSize()[self.index]

    def _getSize(self):
        self.__checkThisIsValid()
        if self.horizontal:
            x = self.__getDrawableSize()
            y = self._getWidth()
        else:
            x = self._getWidth()
            y = self.__getDrawableSize()
        return (x,y)

    def _getFullRect(self):
        self.__checkThisIsValid()
        r = pygame.rect.Rect((0,0), self._getSize())
        self.pos.apply(self.app, r)
        return r

    def __movedTo(self, pos):
        self.__checkThisIsValid()
        if self.horizontal:
            self._setPosition(self.originalPosition + (pos[0] - self.beingDraggedFrom[0]))
        else:
            self._setPosition(self.originalPosition + (pos[1] - self.beingDraggedFrom[1]))
            
        newScrollingPos = self._getPosition() * self.__getCanvasSize() / self.__getDrawableSize()
        newScrollingPos = min(newScrollingPos, self.__getCanvasSize() - self.__getDrawableSize())
        if self.horizontal:
            self.parent.setHorizontalPos(newScrollingPos)
        else:
            self.parent.setVerticalPos(newScrollingPos)

    def _getPosition(self):
        # This line is useful in the event of a screen resize
        self._setPosition(self.position)
        return self.position

    def _setPosition(self, pos):
        self.position = min(max(pos, 0), self.__getDrawableSize() - self._getBarLength())
        

    def processEvent(self, event):
        self.__checkThisIsValid()
        if event.type == pygame.locals.MOUSEBUTTONDOWN and \
           event.button == 1 and self._getBarRect().collidepoint(event.pos) and \
           self.beingDraggedFrom == None:
            self.beingDraggedFrom = event.pos
            return None
        elif event.type == pygame.locals.MOUSEMOTION and self.beingDraggedFrom != None:
            self.__movedTo(event.pos)
            return None
        elif event.type == pygame.locals.MOUSEBUTTONUP and event.button == 1 and self.beingDraggedFrom != None:
            self.beingDraggedFrom = None
            self.originalPosition = self._getPosition()
            return None
        return event

    def draw(self, screen):
        self.__checkThisIsValid()
        pygame.draw.rect(screen, self.backColour, self._getFullRect(), 0)
        pygame.draw.rect(screen, self.colour, self._getBarRect(), 0)
            

class ScrollableCanvas(CompoundElement):
    # For a scrollable canvas, the displaySize is
    # how big it will actually be drawn, while its
    # size is how big the canvas is in memory.
    # If the size is bigger than the displaySize
    # either horizontally or vertically, there will
    # be a scroll bar to allow moving around the
    # full area.


        
    def __init__(self, app, pos, size, displaySize):
        super(ScrollableCanvas, self).__init__(app)

        self.pos = pos
        self.size = size
        self.displaySize = displaySize

        self.__horizontalScrollBar = ScrollBar(app, self, Location(AttachedPoint((0,0), self._getRect, 'bottomleft'), 'bottomleft'), True)        
        self.__verticalScrollBar = ScrollBar(app, self, Location(AttachedPoint((0,0), self._getRect, 'topright'), 'topright'), False)
    
        ## internalPos is the position on the full canvas that we are drawing from
        self._setInternalPos((0,0))

    def _getInternalPos(self):
        # This line is useful in the event of screen resizes:
        self._setInternalPos(self.internalPos)
        
        return self.internalPos

    def _setInternalPos(self, pos):
        self.internalPos = tuple([min(pos[i], (self._getCanvasSize()[i] - self._getDrawableSize()[i])) for i in 0,1])

    def _getHorizontalScrollBar(self):
        if self._needsHorizontalScrollBar():
            return self.__horizontalScrollBar
        return None
    
    def _getVerticalScrollBar(self):
        if self._needsVerticalScrollBar():
            return self.__verticalScrollBar
        return None

    def __calculateIfWeNeedBars(self):
        hasHorizontalScrollBar = self._getMinimumCanvasSize()[0] > self._getSize()[0]
        if hasHorizontalScrollBar:
            hasVerticalScrollBar = self._getMinimumCanvasSize()[1] > self._getSize()[1] - self.__horizontalScrollBar._getWidth()
        else:
            hasVerticalScrollBar = self._getMinimumCanvasSize()[1] > self._getSize()[1]
        if hasVerticalScrollBar and not hasHorizontalScrollBar:
            # re-calculate now that we know we have a vertical scroll bar
            hasHorizontalScrollBar = self._getMinimumCanvasSize()[0] > self._getSize()[0] - self.__verticalScrollBar._getWidth()
        return (hasHorizontalScrollBar, hasVerticalScrollBar)

    def _getDrawableSize(self):
        drawableHeight = self._getSize()[1]

        hasHorizontalScrollBar, hasVerticalScrollBar = self.__calculateIfWeNeedBars()
        
        if hasHorizontalScrollBar:
            drawableHeight -= ScrollBar.defaultWidth
            
        drawableWidth = self._getSize()[0]
        if hasVerticalScrollBar:
            drawableWidth -= ScrollBar.defaultWidth

        return (drawableWidth, drawableHeight)        

    def _needsHorizontalScrollBar(self):
        return self.__calculateIfWeNeedBars()[0]

    def _needsVerticalScrollBar(self):
        return self.__calculateIfWeNeedBars()[1]

    def _getPt(self):
        return self._getRect().topleft

    def _getSize(self):
        return self.displaySize.getSize(self.app)

    def _getMinimumCanvasSize(self):
        return self.size.getSize(self.app)

    def _getCanvasSize(self):
        canvasSize = self._getMinimumCanvasSize()
        availableSize = self._getDrawableSize()
        x = max(availableSize[0], canvasSize[0])
        y = max(availableSize[1], canvasSize[1])
        return x, y


    def _getRect(self):
        r = pygame.rect.Rect((0,0), self._getSize())
        self.pos.apply(self.app, r)
        return r

    def setVerticalPos(self, verticalPos):
        self._setInternalPos((self._getInternalPos()[0], verticalPos))
        
    def setHorizontalPos(self, horizontalPos):
        self._setInternalPos((horizontalPos, self._getInternalPos()[1]))

    def _getContentsRect(self):
        return pygame.rect.Rect(self._getPt(), self._getDrawableSize())

    def _getOffsetCanvasRect(self):
        topleft = self._getPt()
        offsetPt = tuple([topleft[i] - self._getInternalPos()[i] for i in 0, 1])
        return pygame.rect.Rect(offsetPt, self._getCanvasSize())
        
    def draw(self, screen):
        contentsRect = self._getContentsRect()
        screen.fill((64,64,64), contentsRect)
        canvasSize = self.size.getSize(self.app)
        size = self._getSize()
        if self._needsHorizontalScrollBar():
            self._getHorizontalScrollBar().draw(screen)
        if self._needsVerticalScrollBar():
            self._getVerticalScrollBar().draw(screen)
        oldClipRect = screen.get_clip()
        
        if oldClipRect is None:
            screen.set_clip(contentsRect)
        else:
            assert isinstance(oldClipRect, pygame.rect.Rect)
            r = oldClipRect.clip(contentsRect)
            screen.set_clip(r)
        try:
            super(ScrollableCanvas, self).draw(screen)
        finally:
            screen.set_clip(oldClipRect)

       
    def processEvent(self, event):
        if self._needsHorizontalScrollBar():
            event = self._getHorizontalScrollBar().processEvent(event)
        if self._needsVerticalScrollBar() and event:
            event = self._getVerticalScrollBar().processEvent(event)
        if event:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
                if self._getContentsRect().collidepoint(event.pos):
                    super(ScrollableCanvas, self).processEvent(event)
                    return None
                else:
                    return event
            else:
                return super(ScrollableCanvas, self).processEvent(event)
        else:
            return None


def ScrollableCanvasAttachedPoint(scrollableCanvas, val, anchor='topleft'):
    return AttachedPoint(val, scrollableCanvas._getOffsetCanvasRect, anchor)
