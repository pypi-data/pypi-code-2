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

from trosnoth.src.utils.event import Event
from trosnoth.src.gui.common import uniqueColour, Location, AttachedPoint

from trosnoth.src.gui.framework.framework import Element
from trosnoth.src.gui.framework.elements import TextButton
from trosnoth.src.gui.framework.utils import WordWrap
        
class ScrollingText(Element):
    # TODO: stick pictures in?
    # TODO: maybe a weighted speed bar
    # TODO: option to start or end off-screen
    def __init__(self, app, area, text, colour, fonts, bgColour=None,
            textAlign='left', loop=False, startOff=False, antiAlias=False):
        super(ScrollingText,self).__init__(app)

        self.area = area
        self.border = False
        self.loop = loop
        self.startOff = startOff
        self.bgColour = bgColour
        self.speed = 50
        
        self.offset = 0
        self.colour = colour
        self.fonts = fonts
        self.text = text
        self.textAlign = textAlign
        self.antiAlias = antiAlias

        # A test to see whether the size has changed - admittedly, somewhat of a hack
        self.lastSize = app.screenManager.size
        
        self.__setImage()
        
        self.autoScroll = False


        # Create up and down buttons for if there's autoscroll.
        if fonts.has_key('buttons'):
            font = fonts['buttons']
        else:
            font = app.fonts.scrollingButtonsFont
        pos = Location(AttachedPoint((0,0), self._getRect, 'topright'), 'topleft')
        self.upBtn = TextButton(app, pos, ' up', font, colour, (255,255,255))
        pos = Location(AttachedPoint((0,0), self._getRect, 'bottomright'), 'bottomleft')
        self.dnBtn = TextButton(app, pos, ' down', font, colour, (255,255,255))

        self.onFinishedScrolling = Event()

    def setAutoscroll(self, hasAutoscroll):
        self.autoScroll = hasAutoscroll

    def setSpeed(self, speed):
        self.speed = speed

    def setBorder(self, hasBorder):
        self.border = hasBorder

    def __setImage(self):
        text, colour, fonts, align = self.text, self.colour, self.fonts, self.textAlign

        margin = 50
        
        # TODO: fix tab formatting
        lines = text.split('\n')
        rendered = []
        heading1Font = fonts['h1']
        heading2Font = fonts['h2']
        bodyFont = fonts['body']
        x = 0

        width = self._getSize()[0] - 2 * margin
        while x < len(lines):
            line = lines[x]
            if line.startswith("<h1>") and line.endswith("</h1>"):
                style = "h1"
                line = line[4:len(line)-5]
                font = heading1Font
            elif line.startswith("<h2>") and line.endswith("</h2>"):
                style = "h2"
                line = line[4:len(line)-5]
                font = heading2Font
            else:
                style = "body"
                font = bodyFont

            newLines = WordWrap(self.app, line, font, width)
            line = newLines[0]
            del newLines[0]

            # Insert the new lines into the list of lines
            newLines.reverse()
            for l in newLines:
                if style == "h1":
                    l = "<h1>" + l + "</h1>"
                elif style == "h2":
                    l = "<h2>" + l + "</h2>"
                lines.insert(x + 1, l)
                    
                    
            if self.bgColour:
                img = font.render(self.app, line, self.antiAlias, colour,
                        self.bgColour)
            else:
                img = font.render(self.app, line, self.antiAlias, colour)
            rendered.append(img)
            x += 1

        height = 0
        width = self._getSize()[0]
        for r in rendered:
            height += r.get_height()
        
        newImage = pygame.Surface((width, height))
        if self.bgColour:
            newImage.fill(self.bgColour)
        else:
            # TODO: This isn't very nice - need a better way of
            # making it transparent than choosing a colour
            # that doesn't exist. (It's fallible, too, if someone adds
            # a new colour).
            key = uniqueColour((colour),)
            newImage.fill(key)
            newImage.set_colorkey(key)
        yPos = 0
        for r in rendered:
            if align == 'left':
                xPos = margin
            elif align == 'right':
                xPos = width - r.get_width() - margin
            elif align == 'middle':
                xPos = (width - r.get_width()) / 2
            else:
                raise ValueError, "Not a valid alignment argument"
                
            newImage.blit(r, (xPos, yPos))
            yPos += r.get_height()
        if self.startOff:
            if self.loop:
                size = (width, height + self._getSize()[1])
            else:
                size = (width, height + 2 * self._getSize()[1])
        else:
            size = (width, height)
                        
        self.image = pygame.Surface(size)
        if not self.bgColour:
            self.image.fill(key)
            self.image.set_colorkey(key)
        if self.startOff:
            self.image.blit(newImage, (0, self._getSize()[1]))
        else:
            self.image.blit(newImage, (0, 0))

        self.canScroll = self.image.get_height() > self._getSize()[1]
        self.reachedEnd = (not self.loop and self.offset == 0) or (self.loop and not self.canScroll)

    def returnToTop(self):
        self.offset = 0

    def _getRect(self):
        return self.area.getRect(self.app)

    def _getSize(self):
        return self._getRect().size

    def _getPt(self):
        return self._getRect().topleft
            
    def draw(self, screen):
        if self.app.screenManager.size != self.lastSize:
            self.lastSize = self.app.screenManager.size
            self.__setImage()
        if not self.canScroll:
            # Our image won't cover the whole of the scrollingText
            height = self._getSize()[1] - self.image.get_height()
            rect = pygame.Rect(self._getPt()[0], self._getPt()[1] + self.image.get_height(),\
                               self._getSize()[0], height)
            if self.bgColour:
                screen.fill(self.bgColour, rect)
        # Find the segment which will be drawn on screen
        rect = pygame.Rect((0, self.offset), self._getSize())
        screen.blit(self.image, self._getPt(), rect)

        if self.loop and self.canScroll and self.offset + self._getSize()[1] > self.image.get_height():
            # It's doing the looping
            rect = pygame.Rect((0, self.offset - self.image.get_height()), self._getSize())
            screen.blit(self.image, self._getPt(), rect)


        if self.border:
            rect.topleft = self._getPt()
            pygame.draw.rect(screen, (0,0,0), rect, 4)
        
        if not self.autoScroll:
            self.upBtn.draw(screen)
            self.dnBtn.draw(screen)

    def processEvent(self, event):
        if self.autoScroll:
            # We don't consume any events.
            return event
        else:
            event = self.upBtn.processEvent(event)
            if not event: return
            event = self.dnBtn.processEvent(event)
            if not event: return

            return event

    def scroll(self, offset):
        if not self.canScroll:
            return
        if self.reachedEnd:
            if (offset > 0 and self.offset > 0) or \
               (offset < 0 and self.offset == 0):
                   # They have already reached the end, and are trying to
                   # go further that way - do nothing.
                   return
        self.reachedEnd = False
        newOffset = offset + self.offset
        if not self.loop:
            if newOffset + self._getSize()[1] > self.image.get_height():
                # They've hit the bottom
                newOffset = self.image.get_height() - self._getSize()[1]
                self.onFinishedScrolling.execute()
                self.reachedEnd = True
            elif newOffset <= 0:
                # Hit the top
                newOffset = 0
                self.onFinishedScrolling.execute()
                self.reachedEnd = True
        self.offset = newOffset
        
        # For looping: make sure it loops around
        if self.loop:
            self.offset %= self.image.get_height()


    def _getSpeed(self):
        if hasattr(self.speed, 'getSpeed'):
            speed = self.speed.getSpeed(self.app)
        else:
            speed = self.speed
        return speed

    def tick(self, deltaT):
        if self.autoScroll:
            self.scroll(self._getSpeed() * deltaT)
        else:
            if self.upBtn.mouseOver:
                self.scroll(-self._getSpeed() * deltaT)
            elif self.dnBtn.mouseOver:
                self.scroll(self._getSpeed() * deltaT)
            self.upBtn.tick(deltaT)
            self.dnBtn.tick(deltaT)
