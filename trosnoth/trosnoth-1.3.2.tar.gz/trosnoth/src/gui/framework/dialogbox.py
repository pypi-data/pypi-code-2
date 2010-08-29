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
from trosnoth.src.gui.common import translateEvent, Location, addPositions, AttachedPoint
from trosnoth.src.gui.screenManager.windowManager import MultiWindowException
from trosnoth.src.gui.framework.utils import WordWrap
from trosnoth.src.utils.event import Event
from trosnoth.src.utils.utils import new
import pygame


class MoveableBox(CompoundElement):
    defaultBorderColour = (0,0,255)
    defaultTitleColour = (255,255,255)
    defaultBackgroundColour = (255,255,255)

    # The _edge class handles the border (including dragging and dropping)
    # of boxes. It also handles the position of the box (so the box must query
    # the edge to find its top left)
    class Edge(Element):
        def __init__(self, app, box, caption, subCaption = None):
            super(MoveableBox.Edge, self).__init__(app)
            self.box = box
            self.font = app.screenManager.fonts.captionFont
            self.smallFont = app.screenManager.fonts.keymapFont
            self.caption = caption
            self.subCaption = subCaption
            self.beingDragged = False
            self.borderWidth = 3
            appSize = app.screenManager.size
            self._setPos(tuple([(appSize[i] - self._getFullSize()[i]) / 2 for i in 0,1]))

        def _getFullSize(self):
            return (self._getFullWidth(), self.box._getSize()[1] + self.borderWidth + self._getHeaderHeight())
            
        def _setPos(self, pos):
            self.pos = pos
            
        def __movedBy(self, difference):
            self._setPos(addPositions(difference, self.pos))

        def _getInsideTopLeftPt(self):
            return addPositions(self.pos, (self.borderWidth, self._getHeaderHeight()))

        def _getHeaderHeight(self):
            return int(self.font.getLineSize(self.app) * 1.5)

        def _getFullWidth(self):
            return self.box._getSize()[0] + self.borderWidth * 2
            
        def _getHeaderRect(self):
            r = pygame.rect.Rect(self.pos, (self._getFullWidth(), self._getHeaderHeight()))
            return r

        def _getEdgeRect(self):
            return pygame.Rect(self.pos, (self._getFullSize()))

        def processEvent(self, event):
            if event.type == pygame.locals.MOUSEBUTTONDOWN and self._getEdgeRect().collidepoint(event.pos):
                self.box.onFocus.execute()
            if event.type == pygame.locals.MOUSEBUTTONDOWN and event.button == 1 and self._getHeaderRect().collidepoint(event.pos):
                self.beingDragged = True
                return None
            elif event.type == pygame.locals.MOUSEMOTION and self.beingDragged:
                self.__movedBy(event.rel)
                return None
            elif event.type == pygame.locals.MOUSEBUTTONUP and event.button == 1 and self.beingDragged == True:
                self.beingDragged = False
                return None
            return event

        def draw(self, screen):
            screen.fill(self.borderColour, self._getEdgeRect())
            # Make pretty edges:
            setOuterBorder = lambda x, y: min(x + y, 255)
            outerBorder1 = tuple([setOuterBorder(self.borderColour[i], 70) for i in 0,1,2])
            outerBorder2 = tuple([setOuterBorder(self.borderColour[i], 35) for i in 0,1,2])
            pygame.draw.rect(screen, outerBorder1, self._getEdgeRect(), 1)
            if self.borderWidth > 2:
                oldRect = self._getEdgeRect()
                newRect = pygame.rect.Rect(oldRect.left+1, oldRect.top+1, oldRect.width - 2, oldRect.height - 2)
                pygame.draw.rect(screen, outerBorder2, newRect, 1)

            text = self.font.render(self.app, self.caption, True, self.titleColour, self.borderColour)
            if self.subCaption is None:
                height = int(self.font.getLineSize(self.app) * 0.25)
            else:
                height = int(self.font.getLineSize(self.app) * 0.1)
            screen.blit(text, addPositions(self.pos, (self.borderWidth + 5, height)))    
            if self.subCaption is not None:
                subText = self.smallFont.render(self.app, self.subCaption, True, self.titleColour)
                height = int(self.font.getLineSize(self.app) * 0.8)
                screen.blit(subText, addPositions(self.pos, (self.borderWidth + 5, height)))    
    
    
    def __init__(self, app, size, caption, subCaption = None):
        super(MoveableBox, self).__init__(app)
        self.size = size
        self._edge = MoveableBox.Edge(self.app, self, caption, subCaption)
        
        self.setColours(self.defaultBorderColour, self.defaultTitleColour, self.defaultBackgroundColour)
        
        self.onClose = Event()
        self.onFocus = Event()
        self.onFocus.addListener(lambda: self.app.screenManager.dialogFocus(self))

    def _getSize(self):
        if hasattr(self.size, 'getSize'):
            return self.size.getSize(self.app)
        else:
            return self.size
        
    def _setPos(self, pos):
        self._edge._setPos(pos)

    def setColours(self, borderColour = None, titleColour = None, backgroundColour = None):
        if borderColour:
            self._edge.borderColour = borderColour
        if titleColour:
            self._edge.titleColour = titleColour
        if backgroundColour:
            self.backgroundColour = backgroundColour

    def setCaption(self, caption = None, subCaption = None):
        if caption is not None:
            self._edge.caption = caption
        if subCaption is not None:
            if subCaption == False:
                self._edge.subCaption = None
            else:
                self._edge.subCaption = subCaption

    def _getPt(self):
        return self._edge._getInsideArea()

    def _getInsideRect(self):
            return pygame.Rect(self._edge._getInsideTopLeftPt(),
                               self._getSize())
        
    def draw(self, screen):
        self._edge.draw(screen)
        subSurface = pygame.Surface(self._getSize())
        subSurface.fill(self.backgroundColour)
        super(MoveableBox, self).draw(subSurface)
        screen.blit(subSurface, self._edge._getInsideTopLeftPt())
        
    def processEvent(self, event):
        event = self._edge.processEvent(event)
        if event:
            if hasattr(event, 'pos'):
                event2 = translateEvent(event, self._edge._getInsideTopLeftPt())
                isPos = True
            else:
                event2 = event
                isPos = False
            event2 = super(MoveableBox, self).processEvent(event2)
            if event2 == None:
                return None
            elif isPos and self._edge._getEdgeRect().collidepoint(event.pos):
                return None
            else:
                return event

    def Show(self):
        try:
            self.app.screenManager.showDialog(self)
        except AttributeError:
            raise MultiWindowException, "Dialog Boxes cannot be used unless the Application is a MultiWindowApplication"

    def Close(self):
        try:
            self.app.screenManager.closeDialog(self)
        except AttributeError:
            raise MultiWindowException, "Dialog Boxes cannot be used unless the Application is a MultiWindowApplication"
        else:
            self.onClose.execute()
        
class DialogBox(MoveableBox):
    flashTime = 0.3
    flashNum = 2
    def __init__(self, app, size, caption, subCaption = None):
        super(DialogBox, self).__init__(app, size, caption, subCaption)
        self.timeToFlash = 0
        
    def processEvent(self, event):
        event = super(DialogBox, self).processEvent(event)
        if event:
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                # It was clicked, but not within us.
                self.timeToFlash = self.flashNum * self.flashTime * 2
                # (Times 2 because we flash on and off)

            # We want to hold any messages except quit ones
            if event.type == pygame.locals.QUIT:
                return event
        return None

    def tick(self, deltaT):
        if self.timeToFlash > 0:
            self.timeToFlash = max(self.timeToFlash - deltaT, 0)
        super(DialogBox, self).tick(deltaT)

    def draw(self, screen):
        if self.timeToFlash > 0:
            phase = int(self.timeToFlash / self.flashTime) % 2
            if phase == 1 and self.__normalBorderColour == self._edge.borderColour:
                invert = lambda x: tuple([255-i for i in x])
                super(DialogBox, self).setColours(borderColour = invert(self.__normalBorderColour), titleColour = invert(self.__normalTitleColour))
            elif phase == 0 and self.__normalBorderColour != self._edge.borderColour:
                super(DialogBox, self).setColours(borderColour = self.__normalBorderColour, titleColour = self.__normalTitleColour)
        super(DialogBox, self).draw(screen)

    def setColours(self, borderColour = None, titleColour = None, backgroundColour = None):
        super(DialogBox, self).setColours(borderColour, titleColour, backgroundColour)
        self.__normalBorderColour = self._edge.borderColour
        self.__normalTitleColour = self._edge.titleColour
        self.timeToFlash = 0

    def setCaption(self, caption = None, subCaption = None):
        super(DialogBox, self).setCaption(caption, subCaption)

class MessageBox(DialogBox):
    '''buttons = a tuple of DialogResults'''
    def __init__(self, app, size, caption, message, buttons):
        super(MessageBox, self).__init__(app, size, caption)
        if hasattr(size, 'getSize'):
            size = size.getSize(app)
        textFont = app.screenManager.fonts.labelFont
        lines = WordWrap(app, message, textFont, size[0])
        y = 5
        for text in lines:
            textPos = Location(DialogBoxAttachedPoint(self, (0, y), 'midtop'), 'midtop')
            self.elements.append(TextElement(app, text, textFont, textPos))
            y += textFont.getHeight(app)
        buttonFont = app.screenManager.fonts.captionFont
        def getResultLambda(dialogResult):
            return lambda sender: self.__setResultAndClose(dialogResult)
        for x in range(0, len(buttons)):
            dialogResult = buttons[x]
            action = getResultLambda(dialogResult)
            location = Location(DialogBoxAttachedPoint(self, (0, -textFont.getHeight(self.app) / 2), 'midbottom'), 'midbottom')
        buttonFont = app.screenManager.fonts.captionFont
        def getResultLambda(dialogResult):
            return lambda sender: self.__setResultAndClose(dialogResult)
        for x in range(0, len(buttons)):
            dialogResult = buttons[x]
            action = getResultLambda(dialogResult)
            location = Location(((x + 1) * size[0] / (len(buttons) + 1), size[1] * 2 / 3), 'midtop')
            button = TextButton(app, location, DialogResult.text[dialogResult], buttonFont, (255,0,0), (255,100,200))
            button.onClick.addListener(action)
            self.elements.append(button)
        self.result = None
        del getResultLambda

    def GetResult(self):
        return self.result

    def __setResultAndClose(self, result):
        self.result = result
        self.Close()

class YesNoBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.Yes, DialogResult.No)
        super(YesNoBox, self).__init__(app, size, caption, message, buttons)

class YesNoCancelBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.Yes, DialogResult.No, DialogResult.Cancel)
        super(YesNoCancelBox, self).__init__(app, size, caption, message, buttons)

class OkBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = tuple([DialogResult.OK])
        super(OkBox, self).__init__(app, size, caption, message, buttons)

class OkCancelBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.OK, DialogResult.Cancel)
        super(OkCancelBox, self).__init__(app, size, caption, message, buttons)

class OkRetryBox(MessageBox):
    def __init__(self, app, size, caption, message):
        buttons = (DialogResult.OK, DialogResult.Retry)
        super(OkCancelBox, self).__init__(app, size, caption, message, buttons)

class DialogResult(object):
    OK, Cancel, Yes, No, Retry = new(5)
    text = {OK:'OK', Cancel:'Cancel', Yes:'Yes', No:'No', Retry:'Retry'}
    

def getInsideRectFromZero(box):
    r = box._getInsideRect()
    r.topleft = (0,0)
    return r

def DialogBoxAttachedPoint(box, val, anchor='topleft'):
    return AttachedPoint(val, lambda:getInsideRectFromZero(box), anchor)
