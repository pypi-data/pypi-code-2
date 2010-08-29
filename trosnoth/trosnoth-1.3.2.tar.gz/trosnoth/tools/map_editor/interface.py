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

'''interface.py - TODO: I really should explain what this thing does.'''
import pygame
import os

from trosnoth.src.gui.framework import framework, elements, listbox, checkbox
from trosnoth.src.model.mapblocks import ForwardInterfaceMapBlock, InterfaceMapBlock, \
     BackwardInterfaceMapBlock, TopBodyMapBlock, BottomBodyMapBlock, BodyMapBlock
blocks = [ForwardInterfaceMapBlock, BackwardInterfaceMapBlock, TopBodyMapBlock, BottomBodyMapBlock]

from trosnoth.src.gui.fonts.font import ScaledFont
from trosnoth.src.gui.common import FullScreenAttachedPoint, ScaledSize, Location, Area

class Interface(framework.CompoundElement):
    def __init__(self, mapBlockCreator):
        super(Interface, self).__init__(mapBlockCreator)
        self.elements = []
        self.mapBlockCreator = mapBlockCreator
        self.makeElements()

    def makeElements(self):
        bigFont = ScaledFont('FreeSans.ttf', 36)
        smallFont = ScaledFont('FreeSans.ttf', 18)
        self.blockCheck = checkbox.CheckBox(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, 10), 'topleft'), 'topleft'), "Blocked",
                                       bigFont, (0,0,0))
        self.symCheck = checkbox.CheckBox(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, 50), 'topleft'), 'topleft'), "Symmetrical",
                                       bigFont, (0,0,0))
        self.mapBlockType = listbox.ListBox(self.app, Area(FullScreenAttachedPoint(ScaledSize(10, 90), 'topleft'), ScaledSize(200, 100), 'topleft'), \
                                             ["Forward Interface Map Block",
                                              "Backward Interface Map Block",
                                              "Top Body Map Block",
                                              "Bottom Body Map Block"],\
                                             smallFont,
                                             (128,128,128), (0,192,0), False)
        self.quitButton = elements.TextButton(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, -40), 'bottomleft'), 'bottomleft'), "Quit",
                                             bigFont,
                                             (0,0,0), (0,192,0))
        self.quitButton.onClick.addListener(lambda sender: self.cease())
        self.saveButton = elements.TextButton(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, 230), 'topleft'), 'topleft'), "Save",
                                              bigFont,
                                              (0,192,0), (0,230,0))
        self.saveButton.onClick.addListener(lambda sender: self.mapBlockCreator.save())

        self.saveAsButton = elements.TextButton(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, 260), 'topleft'), 'topleft'), "Save As...",
                                                bigFont,
                                                (0,192,0), (0,230,0))
        self.saveAsButton.onClick.addListener(lambda sender: self.mapBlockCreator.saveAs())

        self.loadButton = elements.TextButton(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, 290), 'topleft'), 'topleft'), "Load...",
                                              bigFont,
                                              (0,192,0), (0,230,0))
        self.loadButton.onClick.addListener(lambda sender: self.mapBlockCreator.load())

        self.newButton = elements.TextButton(self.app, Location(FullScreenAttachedPoint(ScaledSize(10, 320), 'topleft'), 'topleft'), "New",
                                              bigFont,
                                              (0,192,0), (0,230,0))
        self.newButton.onClick.addListener(lambda sender: self.mapBlockCreator.newFile())

        

        self.elements = [self.blockCheck, self.symCheck, self.mapBlockType, \
                         self.saveButton, self.saveAsButton, self.loadButton, \
                         self.quitButton, self.newButton]

        # self.correctSelf()

    def cease(self):
        self.mapBlockCreator.stop()
        

    def correctSelf(self):
        self.blockCheck.value = self.mapBlockCreator.currentBlockage
        self.symCheck.value = self.mapBlockCreator.symmetrical
        self.mapBlockType.setIndex(blocks.index(self.mapBlockCreator.currentType))
        
        

    def repositionElements(self):
        pass

    def newScreen(self, screen):
        self.screen = screen
        self.saveScreen = pygame.surface.Surface(self.mapBlockCreator.actualRect.size)
        self.repositionElements()
        self.reDraw()

    def getBlockage(self):
        return self.blockCheck.value

    def getSym(self):
        return self.symCheck.value

    def getMapBlockType(self):
        typeOfBlock = eval(self.mapBlockType.getItem().replace(" ", ""))
        return typeOfBlock

    def newMessage(self, text, colour = None):
        if not colour:
            colour = (128, 128, 128)
        self.messages.newMessage(text, colour)

    def draw(self, surface):
        super(Interface, self).draw(self.screen)
        pygame.draw.rect(self.screen, (0,0,0), self.mapBlockCreator.drawRect, 2)
        for obstacle in self.mapBlockCreator.obstacles:
            if self.mapBlockCreator.moveObstacle.__contains__(obstacle) or\
               (obstacle.mirror and \
                self.mapBlockCreator.moveObstacle.__contains__(obstacle.mirror)):
                continue
            if obstacle != self.mapBlockCreator.changeObstacle[0] and \
               (self.mapBlockCreator.changeObstacle[0] == None or \
               obstacle != self.mapBlockCreator.changeObstacle[0].mirror):
                startPt = self.mapBlockCreator.getRelativePosition(obstacle.startPt)
                endPt = self.mapBlockCreator.getRelativePosition(obstacle.endPt)
                colour = obstacle.getColour()
                pygame.draw.line(self.screen, colour, startPt, endPt, 2)

        #surface.blit(self.screen, (0,0))
                                   

    def reDraw(self, final = False):
        if final:
            self.saveScreen.fill((255,255,255))
        else:
            self.screen.fill((255,255,255))
        for obstacle in self.mapBlockCreator.obstacles:
            if final:
                startPt = obstacle.startPt
                endPt = obstacle.endPt
                pygame.draw.line(self.saveScreen, (255,0,0), startPt, endPt, 2)
            else:
                startPt = self.mapBlockCreator.getRelativePosition(obstacle.startPt)
                endPt = self.mapBlockCreator.getRelativePosition(obstacle.endPt)
                pygame.draw.line(self.screen, (255,0,0), startPt, endPt, 2)
        if not final:
            pygame.draw.rect(self.screen, (0,0,0), self.mapBlockCreator.drawRect, 2)

    def graphify(self, filename):
        self.reDraw(True)
        pygame.image.save(self.saveScreen, filename)
        print filename
        self.reDraw()

    def processEvent(self, event):
        event = super(Interface, self).processEvent(event)
        if not event:
            # The event has been used; redraw the background.
            self.reDraw()
            self.mapBlockCreator.somethingChanged()
        else:
            if event.type == pygame.KEYDOWN:
                self.mapBlockCreator.checkHotkeys(event)
            elif event.type == pygame.KEYUP:
                self.mapBlockCreator.checkHotkeys(event)

            elif event.type == pygame.MOUSEMOTION:
                pos = self.mapBlockCreator.unScaleIt(event.pos)
                self.mapBlockCreator.mouseMove(pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = self.mapBlockCreator.unScaleIt(event.pos)
                self.mapBlockCreator.mouseClick(pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = self.mapBlockCreator.unScaleIt(event.pos)
                self.mapBlockCreator.mouseUp(pos)
        return event
