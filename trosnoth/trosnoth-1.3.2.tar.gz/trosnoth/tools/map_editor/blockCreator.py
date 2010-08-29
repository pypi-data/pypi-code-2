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

'''main.py - I really should explain what this thing does.'''

import Tkinter
import tkFileDialog, tkSimpleDialog
import os

import pygame
import pygame.locals as pgLocals
from math import sin, atan
from copy import copy

from trosnoth.src.model.universe import Universe
from trosnoth.src.model.mapblocks import ForwardInterfaceMapBlock, InterfaceMapBlock, \
     BackwardInterfaceMapBlock, TopBodyMapBlock, BottomBodyMapBlock, BodyMapBlock
from trosnoth.src.model.map import MapLayout
from trosnoth.src.gui.framework import elements, framework
from trosnoth.src.gui import app
from trosnoth.src.utils.utils import new
from trosnoth.src.utils.math import distance
from trosnoth.src.utils.unrepr import unrepr

from trosnoth.data import getPath, makeDirs, user

from trosnoth.tools.map_editor import interface

# TODO: obstacles fly off the end upon copy+paste
# TODO: obstacles should not be on top of each other after paste.
# TODO: allow obstacles that have been selected, to move; rather than selecting
# a new obstacle
# TODO: obstacle selection still assumes obstacles of infinite length
# TODO: check for bugs in alreadySelected stuff; I'm sure I saw one
# TODO: giving options to save and such

# Not so necessary:
# TODO: alreadySelected could take into account mirrors
# TODO: maybe implement side as a property of obstacle; L, R or M
# TODO: give more options of adjustment for mandatory obstacles
# TODO: group in-line obstacles together
# TODO: get rid of alreadySelect when wanting to move

##    The following requirements are based on these values in the universe.
##    Universe class:
##
##    halfZoneHeight = 384
##    zoneBodyWidth = 1024
##    zoneInterfaceWidth = 512
##    halfPlayerSize = (13, 19)


mandatoryEndpoints = {
    ForwardInterfaceMapBlock : (((512, 60), True), ((452, 0), False),
                                ((0, 324), True), ((60, 384), False)),
    BackwardInterfaceMapBlock : (((60, 0), True), ((0, 60), False),
                                 ((452, 384), True), ((512, 324), False)),
     
    TopBodyMapBlock : (((60, 0), True), ((0, 60), False),
                       ((1024, 60), True), ((964, 0), False),
                       ((128, 384), True), ((384, 384), False),
                       ((640, 384), True), ((896, 384), False),
                       ((768, 0), True), ((256, 0), False)),
    BottomBodyMapBlock : (((0, 324), True), ((60, 384), False),
                          ((964, 384), True), ((1024, 324), False),
                          ((384, 0), True), ((128, 0), False),
                          ((896, 0), True), ((640, 0), False),
                          ((256, 384), True), ((768, 384), False))
     }

scales = [1.5, 1.25, 1, 0.75, 0.5]

infinity = new(1)

blockDir = getPath(user, 'blocks')
makeDirs(blockDir)

from math import sqrt, fabs
def lineMagnitude(a, b):
    return sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
# a, b: line endpoints
# c: point
def pointToLine(a, b, c):
    lineMag = lineMagnitude(a, b)
    if lineMag < 0.00000001:
        return 9999999
   
    u = (((c[0] - a[0]) * (b[0] - a[0])) + ((c[1] - a[1]) * (b[1] - a[1])))
    u = u / (lineMag * lineMag)
    if u < 0.00001 or u > 1:
        # Closest point does not fall within the line segment, take the shorter distance
        # to an endpoint
        ix = lineMagnitude(c, a)
        iy = lineMagnitude(c, b)
        if ix > iy:
            return iy
        else:
            return ix
    else:
        # Intersecting point is on the line, use the formula
        ix = a[0] + u * (b[0] - a[0])
        iy = a[1] + u * (b[1] - a[1])
        return lineMagnitude(c, (ix, iy))

def initMenu(mapBlockCreator):
    pass

def gradient(startPt, endPt):
    try:
        grad = (float(startPt[1] - endPt[1])) / (startPt[0] - endPt[0])
    except ZeroDivisionError:
        grad = infinity
    return grad

class inclusiveRect(pygame.rect.Rect):
    # TODO: how do they accept the arguments in Rect?
    def collidepoint(self, *pos):
        x,y = pos
        return (self.left <= x <= self.right) and (self.top <= y <= self.bottom)
        

class Obstacle(object):
    def __init__(self, startPt, endPt, mandatory = False):
        self.startPt = startPt
        self.endPt = endPt
        self.startConnect = None
        self.endConnect = None
        self.length = ((endPt[0] - startPt[0]) ** 2 + \
                      (endPt[1] - startPt[1]) ** 2) ** 0.5
        self.selected = False
        self.tempSelected = False
        self.platform = False
        self.mirror = None
        self.mandatory = mandatory
        self.endpointsChanged()
        # A flag set to true if the obstacle is invalid for some reason.
        self.blackListed = False

    '''def repr(self):
        return "Obstacle <(%s --> %s)>" % (self.startPt, self.endPt)'''

    def togglePlatformity(self, mapBlockCreator):
        if self.endPt[1] == self.startPt[1] and \
           self.startPt[0] < self.endPt[0]:
            self.platform = not self.platform
            mapBlockCreator.platformChange(self)

    def endpointsChanged(self):
        if not (self.endPt[1] == self.startPt[1] and \
           self.startPt[0] < self.endPt[0]) and self.platform:
            self.platform = False
        self.gradient = gradient(self.startPt, self.endPt)
            
    def move(self, change):
        self.moveIt(change)
        if self.mirror and self.mirror != self:
            self.mirror.moveIt((-change[0], change[1]))

    def moveIt(self, change):
        self.startPt = (self.startPt[0] + change[0],
                        self.startPt[1] + change[1])
        self.endPt = (self.endPt[0] + change[0],
                        self.endPt[1] + change[1])

    def getColour(self):
        # Check for colour due to selection:
        if self.selected:
            return (0, 255, 0)
        elif self.tempSelected:
            return (0,0,255)
        elif self.blackListed:
            return (0,0,0)
        # Otherwise check for colour due to orientation
        elif self.platform:
            return (192,0,0)
        elif self.startPt[0] < self.endPt[0]:
            return (255,0,0)
        elif self.endPt[0] < self.startPt[0]:
            return (255,192,0)
        else:
            # TODO: need to show which side is blocked
            return (255, 0, 255)

    def connect(self, obstacle, pt):
        if pt == 0:
            self.startConnect = obstacle
        else:
            self.endConnect = obstacle

    def disconnect(self, pt):
        if pt == 0:
            self.startConnect = None
        else:
            self.endConnect = None

    def point(self, i):
        return (self.startPt, self.endPt)[i]

    def connector(self, i):
        '''Returns a particular connector;
        if i == 0: startConnect,
        if i == 1: endConnect'''
        return (self.startConnect, self.endConnect)[i]
        
class UndoStack(object):
    '''Stack representing the opposite of all the events that have happened.
    These events can be called to undo what has happened.'''
    
    # Number of undos:
    maxSize = 100
    def __init__(self):
        self.clear()

    def undo(self):
        if self.numUndos > 0:
            
            undo = self.undos[self.numUndos - 1]
            del self.undos[self.numUndos - 1]
            self.numUndos -= 1
            # Call the function:
            try:
                undo[0](*undo[1])
            except Exception, e:
                print 'Error in undo: ', e

    def push(self, function, *params):
        self.numUndos += 1
        self.undos.append((function, params))

    def clear(self):
        self.undos = []
        self.numUndos = 0

    def unChanged(self):
        return self.numUndos == 0


class Mode(object):
    Selected, Move, Create, SelectMany, Change, NoMode = new(6)


class MapBlockCreator(app.Application):

    snapDistance = 10
    minLength = 10
    scaleIndex = 3
    def __init__(self):
        super(MapBlockCreator, self).__init__((600,800), 0, "hello", interface.Interface)
        
        self.halfPlayerSize = (22, 22)
        self.undoStack = UndoStack()
        self.scale = scales[self.scaleIndex]
        # User-set options:
        self.changeObstacle = (None, None)
        self.snap = True
        self.obstacles = []
        mainMenu = initMenu(self)
        self.currentPt = None
        self.tempPt = (0, 0)
        self.oldPt = (0, 0)
        self.clickPt = (0,0)
        self.selectRect = None
        self.symmetrical = False
        self.screen = None
        # NOTE: this is linked to the interface's initial block Type;
        #       if you change one, then change the other.
        self.newCreation(ForwardInterfaceMapBlock, False)
        self.straight = False
        self.ctrl = False
        self.endControl = False
        self.selection = []
        self.moveObstacle = []
        self.currentMode = Mode.NoMode
        self.alreadySelected = []
        self.clipboard = []

        self.path = None
        self.graphicName = None
        self.blockName = None

        self.modifiers = {pgLocals.K_LSHIFT : self.toggleShift,
                          pgLocals.K_LCTRL : self.toggleCtrl,
                          pgLocals.K_e : self.toggleEndpoint}

        self.hotkeys = {pgLocals.K_DELETE : self.deleteCurrent,
                        pgLocals.K_r : self.reverseSelected,
                        pgLocals.K_p : self.togglePlatformity,
                        pgLocals.K_PAGEUP : self.scrollUp,
                        pgLocals.K_PAGEDOWN : self.scrollDown,
                        pgLocals.K_F12 : self.saveAs}

        self.controls = {pgLocals.K_o : self.load,
                         pgLocals.K_s : self.save,
                         pgLocals.K_z : self.undo,
                         pgLocals.K_n : self.newFile,
                         pgLocals.K_c : self.copy,
                         pgLocals.K_v : self.paste,
                         pgLocals.K_x : self.cut}

    def somethingChanged(self):
        if self.currentType != self.interface.getMapBlockType():
            if not self.undoStack.unChanged():
                if not self.unsavedCheck():
                    self.interface.correctSelf()
                    return
            toCorrect = False
            if issubclass(self.interface.getMapBlockType(), InterfaceMapBlock) and \
               self.symmetrical:
                self.symmetrical = False
                toCorrect = True
            self.newCreation(self.interface.getMapBlockType(), \
                                  self.interface.getBlockage())
            if toCorrect:
                self.interface.correctSelf()
            if issubclass(self.currentType, InterfaceMapBlock) and \
               self.symmetrical:
                self.symmetrical = False
                self.interface.correctSelf()
        else:
            self.currentBlockage = self.interface.getBlockage()
        if self.symmetrical != self.interface.getSym():
            # Symmetry has changed
            if issubclass(self.currentType, BodyMapBlock):
                self.symmetrical = self.interface.getSym()
            else:
                self.interface.correctSelf()


    def createCopies(self, obstacles):
        tempObstacles = []
        for obstacle in obstacles:
            newObstacle = Obstacle(obstacle.startPt, obstacle.endPt)
            newObstacle.platform = obstacle.platform
            tempObstacles.append(newObstacle)
        return tempObstacles

    def cut(self):
        if len(self.selection) > 0:
            self.clipboard = self.createCopies(self.selection)
            self.deleteCurrent()

    def copy(self):
        if len(self.selection) > 0:
            self.clipboard = self.createCopies(self.selection)

    def paste(self):
        self.cancelCurrent()
        if len(self.clipboard) > 0:
            self.remakeObstacles(self.clipboard)
            for obstacle in self.clipboard:
                self.selection.append(obstacle)
                obstacle.selected = True
            self.currentMode = Mode.Selected
            undoFunction = self.deleteCurrent
            undoParams = self.clipboard
            self.undoStack.push(undoFunction, undoParams)
        

    def scrollUp(self):
        self.changeScale(True)

    def scrollDown(self):
        self.changeScale(False)

    def newCreation(self, typeOfBlock, blocked):
        self.closeCurrentFile()
        self.changeCreateType(typeOfBlock, blocked)
        self.createMandatoryEndpoints()

    def newFile(self):
        self.newCreation(self.currentType, self.currentBlockage)

    def changeScale(self, up):
        drawOffset = (220,20)
        if up == None:
            pass
        elif up and self.scaleIndex < len(scales) - 1:
            self.scaleIndex += 1
        elif not up and self.scaleIndex > 0:
            self.scaleIndex -= 1
        else:
            return
        self.scale = scales[self.scaleIndex]
        scaleWidth = self.actualRect.width / self.scale
        scaleHeight = self.actualRect.height / self.scale
        # drawRect is the graphical representation of the bounds of the mapBlock
        self.drawRect = pygame.rect.Rect(drawOffset, (scaleWidth, scaleHeight))
        size = (self.drawRect.width + drawOffset[0] + 30, \
                self.drawRect.height + drawOffset[1] + 30)
        self.screenManager.setScreenProperties(size, 0, "MapBlock Maker")
        self.screen = self.screenManager.screen
        self.interface.newScreen(self.screen)
        

    def symPoint(self, point):
        return (self.actualRect.width - point[0], point[1])

    def side(self, point):
        '''Returns the side of the rect that this point is on;
        0 = left,
        1 = right'''
        if point[0] < (self.actualRect.width / 2):
            return 0
        else:
            return 1

    
    def drawLine(self, start, end, colour, width = 1):
        realStart = self.getRelativePosition(start)
        realEnd = self.getRelativePosition(end)
        if not self.symmetrical:
            pygame.draw.line(self.screen, colour, realStart, realEnd, width)
        else:
            symStart = self.getRelativePosition(self.symPoint(start))
            symEnd = self.getRelativePosition(self.symPoint(end))
            # If they start and end on the same side:
            if self.side(end) == self.side(start):
                pygame.draw.line(self.screen, colour, realStart, realEnd, width)
                pygame.draw.line(self.screen, colour, symStart, symEnd, width)
            else:
                grad = gradient(realStart, realEnd)
                middle = (self.actualRect.width / 2)
                run = middle - start[0]
                rise = grad * run
                point = self.getRelativePosition((middle, start[1] + rise))
                pygame.draw.line(self.screen, colour, realStart, point, width)
                pygame.draw.line(self.screen, colour, point, symStart, width)

    def unDrawLine(self, start, end, width = 1):
        self.drawLine(start, end, (255,255,255), width)
        

    def changeCreateType(self, blockType, blocked):
        self.currentType = blockType
        self.currentBlockage = blocked
        height = MapLayout.halfZoneHeight
        if issubclass(self.currentType, BodyMapBlock):
            width = MapLayout.zoneBodyWidth
        else:
            width = MapLayout.zoneInterfaceWidth
            
        actualOffset = (0,0)
        playerOffset = self.halfPlayerSize
        playerRectSize = (width - self.halfPlayerSize[0] * 2,
                          height - self.halfPlayerSize[1] * 2)

        # actualRect is the logical representation of the rectangle within
        # which all obstacles have to be
        self.actualRect = pygame.rect.Rect(actualOffset, (width, height))
        # playerRect is the logical representation of the bounds of where
        # non-mandatory obstacles can go.
        self.playerRect = inclusiveRect(playerOffset, playerRectSize)
        self.changeScale(None)
        self.currentBlockage = blocked
        if self.interface:
            self.interface.reDraw()
            self.interface.correctSelf()

    def createMandatoryEndpoints(self):
        '''Creates the endpoints that a valid mapBlock must connect to.
        It is based off self.currentType'''
        for point, entry in mandatoryEndpoints[self.currentType]:
            if point[0] == self.actualRect.left:
                newPoint = (self.actualRect.left + self.halfPlayerSize[0], point[1])
            elif point[0] == self.actualRect.right:
                newPoint = (self.actualRect.right - self.halfPlayerSize[0], point[1])
            elif point[1] == self.actualRect.top:
                newPoint = (point[0], self.actualRect.top + self.halfPlayerSize[1])
            elif point[1] == self.actualRect.bottom:
                newPoint = (point[0], self.actualRect.bottom - self.halfPlayerSize[1])
            else:
                raise ValueError, "Mandatory Endpoint corrupted"
            if entry:
                mand = Obstacle(point, newPoint, True)
            else:
                mand = Obstacle(newPoint, point, True)
            self.obstacles.append(mand)
        if self.symmetrical:
            self.setMirrors()
        

    def getNearbyEndpoint(self, pos, end = None, maxDistance = None):
        '''Returns a nearby endPoint that an obstacle could connect to.
        This procedure will be told which end it must connect to; such that
        a start point cannot connect to another start point (or end to end).
        If the point already has a connection, it will be ignored, such that
        two obstacles cannot connect to the one place.
        Note that the new obstacle can still be on that position, however it
        is not actually logically connected to any other obstacle.

        If end is not given any value, this will mean that it is looking for the
        nearest endpoint of any obstacle, rather than an obstacle itself.

        This procedure will only search items
        that are not in self.alreadySelected. The returning value is added to
        self.alreadySelected. This allows for selecting two obstacles in close
        proximity'''
        
        
        if maxDistance == None:
            maxDistance = self.snapDistance
        maxDistance *= self.scale
        best = (None, maxDistance, None)
        if end == None:
            endsToCheck = (0,1)
        else:
            endsToCheck = [(end + 1) % 2]

        # If there is only one obstacle selected, check this one first.
        if len(self.selection) == 1:
            obstacle = self.selection[0]
            for checkEnd in endsToCheck:
                pt = obstacle.point(checkEnd)
                if self.playerRect.collidepoint(*pt):
                    dist = distance(pos, pt)
                    if dist <= best[1]:
                        best = (obstacle, dist, checkEnd)
            
        if not best[0]:
            for checkEnd in endsToCheck:
                for obstacle in self.obstacles:
                    # Don't select mandatory obstacles if we're wanting to
                    # change
                    if obstacle.mandatory and end == None:
                        continue
                    # TODO: maybe allow this
                    # Don't select obstacles that cross the middle just yet, if
                    # wanting to change
                    if obstacle.mirror == obstacle and end == None:
                        continue
                    # Don't select an obstacle currently being changed
                    if obstacle == self.changeObstacle[0]:
                        continue
                    # Don't select platforms if we're wanting to connect
                    if obstacle.platform and end != None:
                        continue
                    if not obstacle.connector(checkEnd) or end == None:
                        pt = obstacle.point(checkEnd)
                        # Do not check extra-playerRect points.
                        if self.playerRect.collidepoint(*pt):
                            dist = distance(pos, pt)
                            if dist <= best[1]:
                                best = (obstacle, dist, checkEnd)


            
        if end == None:
            return (best[0], best[2])
        else:
            return best[0]

    def getObstacleByPoint(self, pos, selectAgain = True, obstacleSet = None):
        best = (None, self.snapDistance * self.scale)

        if obstacleSet:
            obstaclesToSearch = obstacleSet
        else:
            obstaclesToSearch = self.obstacles
            
        
        for obstacle in obstaclesToSearch:
            if not selectAgain and obstacle in self.alreadySelected:
                continue
            distance = pointToLine(obstacle.startPt, obstacle.endPt, pos)
            if distance < best[1]:
                best = (obstacle, distance)

        if best[0] == None and not selectAgain:
            # If we didn't get any results, check the values 
            returnObs = self.getObstacleByPoint(pos, selectAgain = True,
                                          obstacleSet = self.alreadySelected)
            self.alreadySelected = []
            if returnObs:
                self.alreadySelected.append(returnObs)

        else:
            returnObs = best[0]
            
        if best[0] != None and not selectAgain:
            self.alreadySelected.append(best[0])

        return returnObs

    def getObstaclesInArea(self, rect):
        tempObstacles = []
        for obstacle in self.obstacles:
            if rect.collidepoint(obstacle.startPt) or \
               rect.collidepoint(obstacle.endPt):
                tempObstacles.append(obstacle)
        return tempObstacles

    def selectTheMany(self):
        left, top = [min(self.currentPt[i], self.tempPt[i]) for i in 0,1]
        width, height = [abs(self.tempPt[i] - self.currentPt[i]) for i in 0,1]
        selectRect = pygame.rect.Rect(left, top, width, height)
        
        for obstacle in self.obstacles:
            obstacle.tempSelected = False
            
        for obstacle in self.getObstaclesInArea(selectRect):
            self.selection.append(obstacle)
            obstacle.selected = True

        self.eliminateMirrorsFromSelected()

        self.interface.reDraw()

    def obstaclesStillInside(self, change):
        '''Checks to see whether all the obstacles being moved are still
        within their bounds'''
        if self.symmetrical:
            side = self.side(self.currentPt)
            if side == 0:
                tempRect = pygame.rect.Rect(self.playerRect.topleft,
                                            (self.playerRect.width / 2,
                                             self.playerRect.height))
            else:
                tempRect = pygame.rect.Rect(self.playerRect.midtop,
                                            (self.playerRect.width / 2,
                                             self.playerRect.height))
        else:
            tempRect = self.playerRect
            
        for obstacle in self.moveObstacle:
            if obstacle.mandatory:
                continue
            newStart = [change[i] + obstacle.startPt[i] for i in 0,1]
            newEnd = [change[i] + obstacle.endPt[i] for i in 0,1]
            if not tempRect.collidepoint(*newStart) or \
               not tempRect.collidepoint(*newEnd):
                return False
        return True
            
        
    def reverse(self, obstacle):
        '''Reverse the given obstacle'''
        obstacle.endPt, obstacle.startPt = (obstacle.startPt, obstacle.endPt)
        obstacle.endpointsChanged()
        self.resetConnections(obstacle, 0)

    def reverseSelected(self):
        '''Reverse all selected obstacles'''
        if self.currentMode == Mode.Selected:
            self.reverseThem(self.selection)

            # Set it up for undoing
            undoFunction = self.reverseThem
            undoParams = self.selection
            self.undoStack.push(undoFunction, undoParams)
        

    def reverseThem(self, toReverse):
        for obstacle in toReverse:
            if obstacle.mandatory:
                continue
            self.reverse(obstacle)
            if obstacle.mirror:
                self.reverse(obstacle.mirror)

    def eliminateMirrorsFromSelected(self):
        '''Will ensure that the only obstacles selected are from one side'''
        if not self.symmetrical:
            return
        if self.selection == []:
            return
        side = self.side(self.selection[0].startPt)
        for obstacle in self.selection:
            if obstacle.mirror and obstacle.mirror != obstacle and \
               self.selection.__contains__(obstacle.mirror):
                # TODO: Find the one on the appropriate side
                if self.side(obstacle.startPt) == side:
                    self.deselectObstacle(obstacle.mirror)
                else:
                    self.deselectObstacle(obstacle)
                
                    
            
    def togglePlatformity(self):
        '''Called by the menu (or hotkey). Tells the obstacle(s) that they
        should toggle their platformability, if possible.'''
        if self.currentMode == Mode.Selected:
            self.togglePlatforms(self.selection)

            # Set it up for undoing
            undoFunction = self.togglePlatforms
            undoParams = self.selection
            self.undoStack.push(undoFunction, undoParams)
        

    def togglePlatforms(self, toToggle):
        for obstacle in toToggle:
            if obstacle.mandatory:
                continue
            obstacle.togglePlatformity(self)
            if obstacle.mirror and not obstacle.mirror == obstacle:
                obstacle.mirror.togglePlatformity(self)
        
    

    def platformChange(self, obstacle):
        if obstacle.platform:
            self.deleteConnections(obstacle)
        else:
            self.resetConnections(obstacle, 0)
            
    def deselectObstacle(self, obstacle):
        '''Removes an obstacle from the list of selecteds'''
        self.selection.remove(obstacle)
        obstacle.selected = False
        if self.selection == []:
            self.currentMode = Mode.NoMode
    
    def obstacleSelected(self, obstacle, pos = None):
        '''Sets the given obstacle as the currently selected one'''
        if obstacle == None:
            self.cancelCurrent()
            return

        # In the case of symmetrical mapBlocks, only allow selection on one side
        if obstacle.mirror and self.selection != [] and \
           self.side(obstacle.startPt) != self.side(self.selection[0].startPt):
            obstacle = obstacle.mirror
            
                
        if self.selection.__contains__(obstacle):
            if self.straight:
                # This obstacle was clicked again. Remove it from the selecteds
                self.deselectObstacle(obstacle)
            else:
                # This obstacle was clicked again.
                self.currentMode = Mode.Move
                self.moveObstacle = self.selection
                self.currentPt = pos
        elif obstacle.mirror and self.selection.__contains__(obstacle.mirror):
            # The mirror's obstacle was clicked. Turn it blue by setting
            # tempSelected, but do nothing about it logically.
            obstacle.tempSelected = True
        else:
            if self.straight:
                self.selection.append(obstacle)
                obstacle.selected = True
                self.currentMode = Mode.Selected
            else:
                self.cancelCurrent()
                self.selection = [obstacle]
                obstacle.selected = True
                self.currentMode = Mode.Selected


    def deleteConnections(self, obstacle):
        if obstacle.startConnect:
            obstacle.startConnect.endConnect = None
            obstacle.startConnect = None
        if obstacle.endConnect:
            obstacle.endConnect.startConnect = None
            obstacle.endConnect = None

    def resetConnections(self, obstacle, snap = 5):
        oldStart = obstacle.startConnect
        oldEnd = obstacle.endConnect
        self.deleteConnections(obstacle)
        change = None
        startCon = self.getNearbyEndpoint(obstacle.startPt, 0, snap)
        if startCon:
            obstacle.connect(startCon, 0)
            startCon.connect(obstacle, 1)
            change = [startCon.endPt[i] - obstacle.startPt[i] for i in (0, 1)]
            obstacle.move(change)

        # End snapping gets no tolerance of movement; it must link up exactly
        # based on whatever the startConnection had
        endCon = self.getNearbyEndpoint(obstacle.endPt, 1, 0)
        if endCon:
            if self.isCircular(obstacle, endCon):
                pass
            else:
                obstacle.connect(endCon, 1)
                endCon.connect(obstacle, 0)
                obstacle.point(0)
        self.interface.reDraw()
        # FIXME: If it was exactly right in the first place, this will allow
        # for multiple obstacles to be moved again
        if change == [0,0]:
            change = None
        return change

    def unsavedCheck(self):
        # TODO:
        # "You will lose all changes. Continue?"
        return True

    def mouseClick(self, pos, buttonNum):
        self.clickPt = pos
        if buttonNum == 3:
            self.cancelCurrent()
        # TODO: Check menus
        elif buttonNum == 4:
            self.mouseScroll(True)
        elif buttonNum == 5:
            self.mouseScroll(False)
        
        
        elif self.ctrl:
            if not self.straight:
                self.cancelCurrent()
            self.currentMode = Mode.SelectMany
            self.currentPt = pos

        elif self.endControl:
            obstacleToRedo, end = self.getNearbyEndpoint(pos)
            self.cancelCurrent()
            if obstacleToRedo and end != None:
                self.changeObstacle = (obstacleToRedo, end)
                otherEnd = (end + 1) % 2
                self.currentPt = obstacleToRedo.point(otherEnd)
                self.currentMode = Mode.Change
                self.drawLine(self.currentPt, obstacleToRedo.point(end),
                                 (255,255,255), 3)
            
            
        elif self.currentMode == Mode.Selected and buttonNum == 1:
            nextSelection = self.getObstacleByPoint(pos, selectAgain = False)
            self.obstacleSelected(nextSelection, pos)
            
        elif pos and self.playerRect.collidepoint(*pos) and buttonNum == 1 and \
             self.currentMode == Mode.NoMode:
            if self.snap:
                connect = self.getNearbyEndpoint(pos, 0)
                if connect:
                    pos = connect.endPt

            self.currentPt = pos
            self.currentMode = Mode.Create

    def mouseMove(self, pos):
        if self.currentMode == Mode.Move:
            self.oldPt = self.tempPt
            relPos = [pos[i] - self.currentPt[i] for i in (0,1)]
            oldRelPos = [self.oldPt[i] - self.currentPt[i] for i in (0,1)]
            if self.obstaclesStillInside(relPos):
                self.tempPt = pos
                for moved in self.moveObstacle:
                    if moved.mandatory:
                        continue
                    # Update the moving of the obstacle
                    oldStart = [oldRelPos[i] + moved.startPt[i] for i in 0,1]
                    oldEnd = [oldRelPos[i] + moved.endPt[i] for i in 0,1]
                    self.unDrawLine(oldStart, oldEnd, 2)
                    
                    newStart = [relPos[i] + moved.startPt[i] for i in 0,1]
                    newEnd = [relPos[i] + moved.endPt[i] for i in 0,1]
                    self.drawLine(newStart, newEnd, (0,255,0))
                
        elif self.playerRect.collidepoint(*pos):
            self.oldPt = self.tempPt
            if self.straight and \
                 self.currentMode in (Mode.Create, Mode.Change):
                self.tempPt = self.makeStraight(self.currentPt, pos)[0]
                try:
                    theta = atan(abs(pos[0] - self.currentPt[0]) / \
                                 abs(pos[1] - self.currentPt[1]))
                except ZeroDivisionError:
                    self.tempPt = (self.currentPt[0], pos[1])
                else:
                    if theta > 0.78539816339744828: # atan(1): 45 degrees
                        self.tempPt = (pos[0], self.currentPt[1])
                    else:
                        self.tempPt = (self.currentPt[0], pos[1])
            else:
                self.tempPt = pos
                

            if self.currentMode in (Mode.Create, Mode.Change):
                # Update the line being drawn
                self.unDrawLine(self.currentPt, self.oldPt)
                self.drawLine(self.currentPt, self.tempPt, (255,0,0))

        # To select many, we don't enforce inside-the-boxness (yet)
        # Makes it possible to select those that are exactly on the edge.
        # Perhaps we could eventually enforce this, but that would require
        # us to change how we look for obstacles within the area
        if self.currentMode == Mode.SelectMany:
            self.oldPt = self.tempPt
            self.tempPt = pos
            self.updateSelectMany()

    def rectDraw(self, rect, colour, width = 1):
        topLeft = self.getRelativePosition(rect.topleft)
        size = (rect.width / self.scale, rect.height / self.scale)
        newRect = pygame.rect.Rect(topLeft, size)
        pygame.draw.rect(self.screen, colour, newRect, width)

    def updateSelectMany(self):
        # Erase last rect drawn:
        if self.selectRect:
            self.rectDraw(self.selectRect, (255,255,255), 2)
        left, top = [min(self.currentPt[i], self.tempPt[i]) for i in 0,1]
        width, height = [abs(self.tempPt[i] - self.currentPt[i]) for i in 0,1]
        self.selectRect = pygame.rect.Rect(left, top, width, height)
        self.rectDraw(self.selectRect, (0,0,0), 2)
        
        for obstacle in self.obstacles:
            obstacle.tempSelected = False
        for obstacle in self.getObstaclesInArea(self.selectRect):
            obstacle.tempSelected = True

    def moveObstacles(self, obstacles, relPos):
            snap = 5
            for obstacle in obstacles:
                if obstacle.mandatory:
                    continue
                obstacle.move(relPos)
                change = self.resetConnections(obstacle, snap)
                if change:
                    for obstacle2 in self.moveObstacle:
                        if not obstacle == obstacle2 and \
                           not obstacle.mandatory:
                            obstacle2.move(change)

                    try:
                        assert snap != 0
                    except AssertionError:
                        raise ValueError, "Check this file for bug info"
                        # If this has errored, it must mean that two obstacles
                        # have moved different distances. That shouldn't be
                        # possible.
                    snap = 0

    def mouseUp(self, pos):
        if self.currentMode == Mode.Move:
            # Ensure that it has moved:
            if pos == self.clickPt:
                self.currentMode = Mode.Selected
                return
            
            # Drop moved obstacles
            relPos = [self.tempPt[i] - self.currentPt[i] for i in (0,1)]
            
            self.moveObstacles(self.moveObstacle, relPos)
            # Set it up for undoing
            undoFunction = self.moveObstacles
            undoParams = self.moveObstacle, tuple([-relPos[i] for i in 0,1])
            self.undoStack.push(undoFunction, *undoParams)
            
            self.moveObstacle = []
            self.interface.reDraw()
            self.currentMode = Mode.Selected

        elif self.currentMode == Mode.SelectMany:
            self.selectTheMany()
            if self.selection != []:
                self.currentMode = Mode.Selected
            else:
                self.currentMode = Mode.NoMode
            
        elif self.currentMode in (Mode.Create, Mode.Change):
            if distance(pos, self.clickPt) < self.minLength:
                obstacleSelected = self.getObstacleByPoint(pos,
                                                           selectAgain = False)
                if obstacleSelected:
                    self.obstacleSelected(obstacleSelected, pos)
                else:
                    self.cancelCurrent()
                return
            
            # Make an obstacle
            start, end = self.currentPt, pos

            # If we have been moving a startPoint, swap our values of start
            # and end (as from now on, it is assumed that the current mouse
            # position is the end of the obstacle).
            mand = False
            if self.currentMode == Mode.Change:
                if self.changeObstacle[1] == 0:
                    start, end = (end, start)
                mand = self.changeObstacle[0].mandatory
            # 1. If it is outside, put the endpoint back in the box.
            if not self.playerRect.collidepoint(*end) and not mand:
                end = self.tempPt
                
            # 2. Get the actual positions for making this obstacle:
            start, end = self.getActualPos(start, end, mand)
            
            # 3. If it is long enough, make the obstacle
            if distance(start, end) >= self.minLength:
                
                # Now create the obstacle
                self.makeObstacle(start, end, mand)

                if self.currentMode == Mode.Change:
                    self.removeObstacle(self.changeObstacle[0])
                    # Set it up for undoing
                    undoFunction = self.undoChange
                    undoParams = self.changeObstacle[0]
                    self.undoStack.push(undoFunction, undoParams)
                    self.changeObstacle = (None, None)
                    self.interface.reDraw()

                # Erase the "real-time line"
                self.unDrawLine(self.currentPt, self.tempPt)
                # Set mode back to nothing
            self.currentMode = Mode.NoMode
        self.currentPt = None

    def mouseScroll(self, up):
        if self.ctrl:
            self.changeScale(up)
        

    def undoChange(self, obstacle):
        '''Called to undo the movement of an endpoint.'''
        # First put the obstacle back in its rightful place
        self.remakeObstacles(tuple([obstacle]))
        # Now get rid of the moved one (which will be stored as the previous
        # undo)
        self.undoStack.undo()
        
        
    def makeStraight(self, start, end):
        '''Returns the start and endpoint after having been snapped to either
        vertical or horizontal. Will also return the direction that it
        snapped'''
        
        try:
            theta = atan(abs(end[0] - start[0]) / \
                         abs(end[1] - start[1]))
        except ZeroDivisionError:
            end = self.makeHorizontal(start, end)
            direction = 'ver'
        else:
            if theta > 0.78539816339744828: # atan(1): 45 degrees
                end = self.makeHorizontal(start, end)
                direction = 'hor'
            else:
                end = self.makeVertical(start, end)
                direction = 'ver'
        return start, end, direction

    def makeHorizontal(self, start, end):
        return (end[0], start[1])

    def makeVertical(self, start, end):
        return (start[0], end[1])

    def snapIt(self, start, end, direction = None):
        '''Snaps the start and end points to an appropriate position, based
        on whether there is another obstacle close to the endpoint.'''
        # 1. Find a nearby obstacle endpoint to connect to
        connect = None
        if self.snap:
            connect = self.getNearbyEndpoint(end, 1)

            # 1b. If it exists, snap it
            if connect:
                end = connect.startPt

                # 1c. Ensure the line stays straight if necessary, by
                # retroactively snapping the startPoint
                if direction:
                    if direction == 'ver':
                        start = (end[0], start[1])
                    else:
                        start = (start[0], end[1])
                    self.interface.reDraw()
        return start, end

    def getActualPos(self, start, end, mandatory):
        '''Based on current mapBlock state, determines the points that an
        obstacle will actually be made.'''
        # If the obstacle is at a set angle (vertical, horizontal, etc), it
        # will be stored in the direction variable.
        direction = None
        
        # 1. Make the line the correct straightness
        if self.straight or mandatory:
            start, end, direction = self.makeStraight(start, end)

        # 2. Check to see if we need to snap this obstacle to an obstacle
        if not mandatory:
            start, end = self.snapIt(start, end, direction)

        return start, end
                    
    def remakeObstacles(self, obstacles):
        for obstacle in obstacles:
            self.obstacles.append(obstacle)
            self.resetConnections(obstacle)
            if not self.symmetrical:
                continue
            
            if obstacle.mirror and obstacle.mirror != obstacle:
                self.obstacles.append(obstacle.mirror)
            elif not obstacle.mirror:
                self.makeMirror(obstacle)


    def makeMirror(self, obstacle):
        if obstacle.mirror != None:
            raise Exception, "Obstacle should not already have a mirror"
        # Create the mirror
        symStart = self.symPoint(obstacle.startPt)
        symEnd = self.symPoint(obstacle.endPt)
        
        if symStart == obstacle.endPt:
            obstacle.mirror = obstacle
            return obstacle
        else:
            newObstacle = Obstacle(symEnd, symStart)
            self.resetConnections(newObstacle)
            self.obstacles.append(newObstacle)
            obstacle.mirror = newObstacle
            newObstacle.mirror = obstacle
        return newObstacle
                
                
                

    def makeObstacle(self, start, end, mandatory):
        newObstacles = []
        if not self.symmetrical:
            newObstacles.append(Obstacle(start, end))
        # If it's symmetrical, create two obstacles
        else:
            symStart = self.symPoint(start)
            symEnd = self.symPoint(end)
            # If they start and end on the same side:
            if self.side(end) == self.side(start):
                newObstacles.append(Obstacle(start, end, mandatory))
                newObstacles.append(Obstacle(symEnd, symStart, mandatory))
                newObstacles[0].mirror = newObstacles[1]
                newObstacles[1].mirror = newObstacles[0]
            else:
                grad = gradient(start, end)
                middle = (self.actualRect.width / 2)
                run = middle - start[0]
                rise = grad * run
                point = self.roundPos((middle, start[1] + rise))
                newObstacles.append(Obstacle(start, point, mandatory))
                newObstacles.append(Obstacle(point, symStart, mandatory))
                newObstacles[0].mirror = newObstacles[1]
                newObstacles[1].mirror = newObstacles[0]
                toCheck = newObstacles
        for newObstacle in newObstacles:
            # FIXME: I suspect this will create an issue with the two obstacles
            # meeting at the middle
            self.resetConnections(newObstacle)
            self.obstacles.append(newObstacle)
        self.interface.reDraw()
        self.connectAligned(newObstacles)

        # Set it up for undoing
        if not self.obstacles.__contains__(newObstacles[0]):
            undoParams = self.obstacles[len(self.obstacles) - 1]
        else:
            undoParams = newObstacles[0]
        undoFunction = self.removeObstacle
        self.undoStack.push(undoFunction, undoParams)



    def isCircular(self, thisObstacle, endObstacle):
        '''Given an obstacle, and one it wants to connect to at its endpoint,
        this function will return whether or not this will cause circularity'''
        while endObstacle.endConnect:
            endObstacle = endObstacle.endConnect
        # We should now have the final connection.
        if endObstacle == thisObstacle:
            # It's a circular connection.
            return True
        else:
            return False
            
    def cancelCurrent(self):
        if self.currentPt:
            self.currentPt = None
            self.selectRect = None
        for selectedObstacle in self.selection:
            selectedObstacle.selected = False
        for selectedObstacle in self.selection:
            selectedObstacle.selected = False
        self.changeObstacle = (None, None)
        self.moveObstacle = []
        self.selection = []
        self.currentMode = Mode.NoMode
        self.interface.reDraw()


    def roundPos(self, pos):
        '''Rounds to nearest 1'''
        newPos = tuple([int(pos[i]) for i in 0,1])
        return newPos

    def checkHotkeys(self, event):
        try:
            function = self.modifiers[event.key]
        except KeyError:
            if event.type == pgLocals.KEYDOWN:
                if self.ctrl:
                    try:
                        function = self.controls[event.key]
                    except KeyError:
                        pass
                    else:
                        function()
                else:
                    try:
                        function = self.hotkeys[event.key]
                    except KeyError:
                        pass
                    else:
                        function()
        else:
            function(event.type == pgLocals.KEYUP)

    def toggleShift(self, up):
        self.straight = not up
        self.mouseMove(pygame.mouse.get_pos())

    def toggleCtrl(self, up):
        self.ctrl = not up

    def toggleEndpoint(self, up):
        self.endControl = not up

    def deleteCurrent(self, obstacles = None):
        if not obstacles:
            if self.currentMode == Mode.Selected:
                obstacles = self.selection
            elif self.currentMode == Mode.Move:
                obstacles = self.moveObstacle
        if not obstacles:
            return
        undoParams = []
        for obstacle in obstacles:
            if obstacle.mandatory:
                continue
            undoParams.append(obstacle)
            self.removeObstacle(obstacle)
        self.cancelCurrent()
        self.interface.reDraw()
            
        # Set it up for undoing
        undoFunction = self.remakeObstacles
        undoParams = tuple(undoParams)
        self.undoStack.push(undoFunction, undoParams)

    def removeObstacle(self, obstacle):
        self.obstacles.remove(obstacle)
        self.deleteConnections(obstacle)
        if obstacle.mirror and not obstacle.mirror == obstacle:
            self.obstacles.remove(obstacle.mirror)
            self.deleteConnections(obstacle.mirror)



        
    def getMapBlockString(self):
        # Look only for non-start-pt ones
        allObstacles = []
        allPlatforms = []
        currentSet = []
        for obstacle in self.obstacles:
            if not isinstance(obstacle.connector(0), Obstacle):
                if obstacle.platform:
                    allPlatforms.append((obstacle.startPt, \
                                    obstacle.endPt[0] - obstacle.startPt[0]))
                    continue
                currentSet.append(obstacle.startPt)
                nextObstacle = obstacle
                while isinstance(nextObstacle, Obstacle):
                    currentSet.append(nextObstacle.endPt)
                    nextObstacle = nextObstacle.connector(1)
                allObstacles.append(tuple(currentSet))
                currentSet = []
                
        output = {
            'blockType': self.currentType.__name__,
            'blocked': self.currentBlockage,
            'symmetrical': self.symmetrical,
            'obstacles': allObstacles,
        }
        if allPlatforms != []:
            output['platforms'] = allPlatforms
        return repr(output)

    def save(self):
        if not (self.path and self.graphicName and self.blockName):
            self.saveAs()
        else:
            self.saveInternal()

    def saveInternal(self):
        try:
            graphicPath = os.path.join(blockDir, self.graphicName)
            self.interface.graphify(graphicPath)
            blockPath = os.path.join(blockDir, self.blockName)
            file = open(blockPath,'w')
            outputStr = self.getMapBlockString()
            file.write(outputStr)
        except Exception, E:
            print 'something went wrong:', E

        try:
            file.close()
        except:
            pass

    def saveAs(self):
        tk = Tkinter.Tk()
        #tk.withdraw()

        filename = tkSimpleDialog.askstring('Filename',
                        'Please enter a filename', parent=tk)
        try:
            tk.destroy()
        except:
            # meh
            pass

        if filename == None:
            # Cancel was pressed.
            return

        self.graphicName = filename + imgExt
        self.blockName = filename + blockExt
        self.path = blockDir
        self.saveInternal()

    def load(self):
        try:
            tk = Tkinter.Tk()
            tk.withdraw()
    
            filename = tkFileDialog.askopenfilename(
                        parent=tk,
                        initialdir = blockDir,
                        defaultextension=blockExt, \
                        filetypes=[('Block File', '*.block')])
            tk.destroy()
    
            # Read the file and create the block
            try:
                f = open(filename, 'U')
            except:
                return
            try:
                contents = f.read()
            finally:
                f.close()
            
            try:
                contents = unrepr(contents)
            except:
                raise IOError, 'invalid file format'
            self.loaded(filename, contents)
        except IOError, e:
            print e
            self.closeCurrentFile()
            self.interface.reDraw()

        

        

    def loaded(self, filename, contents):
        blockType = blockFileNamespace[contents.get('blockType', TopBodyMapBlock)]
        blocked = contents.get('blocked', False)
        obstacles = contents.get('obstacles', [])
        platforms = contents.get('platforms', [])
        symmetrical = contents.get('symmetrical', False)

        try:
            self.closeCurrentFile()
            for connectSet in obstacles:
                currentPt = None
                lastObstacle = None
                for point in connectSet:
                    if currentPt:
                        newObstacle = Obstacle(currentPt, point)
                        if lastObstacle:
                            newObstacle.startConnect = lastObstacle
                            lastObstacle.endConnect = newObstacle
                        lastObstacle = newObstacle
                        self.obstacles.append(newObstacle)
                    currentPt = point

            for platform in platforms:
                point = platform[0]
                deltaX = platform[1]
                endPt = (point[0] + deltaX, point[1])
                newObstacle = Obstacle(point, endPt)
                newObstacle.platform = True
                self.obstacles.append(newObstacle)

            for obstacle in self.obstacles:
                self.resetConnections(obstacle, 0)
            self.symmetrical = symmetrical
            self.changeCreateType(blockType, blocked)
            self.setMandatoryFromLoad()
            self.path, self.blockName = self.extractPartsOfFilename(filename)
            self.graphicName = self.extractFilename(self.blockName) + imgExt

        except ValueError:
            raise IOError, "Something didn't load correctly"
        
    def extractPartsOfFilename(self, filename):
        i = -1
        try:
            # TODO: is this right?
            while filename[i] != os.sep and filename[i] != os.altsep:
                i -= 1
        except IndexError:
            raise IOError, "This filename doesn't seem valid"
        else:
            path = filename[:i + 1]
            name = filename[i + 1:]
            return (path, name)

    def extractFilename(self, filename):
        i = -1
        try:
            while filename[i] != '.':
                i -= 1
        except IndexError:
            # No extension. Return as is
            return filename
        name = filename[:i]
        print 'name: ', name
        return name

    def closeCurrentFile(self):
        '''Provides all the necessary clean-up, so that attributes from
        a previously open file don't interfere with another'''
        self.graphicName = None
        self.blockName = None
        self.path = None
        self.obstacles = []
        self.selectRect = None
        self.selection = []
        self.moveObstacle = []
        self.currentMode = Mode.NoMode
        self.undoStack.clear()

    def setMirrors(self, obstacles = None):
        if not obstacles:
            obstacles = self.obstacles
        for obstacle in obstacles:
            if not obstacle.mirror:
                mirror = self.findMirror(obstacle)
                if not mirror:
                    mirror = self.makeMirror(obstacle)
                    mirror.blackListed = True
                obstacle.mirror = mirror
                mirror.mirror = obstacle
                

    def findMirror(self, searchObs):
        mirrorEnd = self.symPoint(searchObs.startPt)
        mirrorStart = self.symPoint(searchObs.endPt)
        for obstacle in self.obstacles:
            if obstacle.startPt == mirrorStart and \
               obstacle.endPt == mirrorEnd and not obstacle.mirror:
                return obstacle
        print "The block claims to be symmetrical but it's not"
        # raise IOError, "The block claims to be symmetrical but it's not"


    def getRelativePosition(self, pos):
        '''Gets an actual position argument, and returns where this point
        should be drawn'''
        scalePos = (pos[0] / self.scale, pos[1] / self.scale)
        relPos = tuple([scalePos[i] + self.drawRect.topleft[i] for i in 0,1])
        roundPos = self.roundPos(relPos)
        return roundPos

    def unScaleIt(self, pos):
        '''Gets a scaled-down position argument, and returns where this point
        actually lies.'''
        relPos = [pos[i] - self.drawRect.topleft[i] for i in 0,1]
        scalePos = (relPos[0] * self.scale, relPos[1] * self.scale)
        roundPos = self.roundPos(scalePos)
        return roundPos

    def undo(self):
        self.undoStack.undo()
        self.interface.reDraw()

    def setMandatoryFromLoad(self):
        '''Derives which obstacles are the mandatory ones from the list
        of obstacles'''
        mandEnd = list(mandatoryEndpoints[self.currentType])
        for obstacle in self.obstacles:
            for point, entry in mandEnd:
                if entry:
                    if obstacle.startPt == point:
                        obstacle.mandatory = True
                        mandEnd.remove((point, entry))
                else:
                    if obstacle.endPt == point:
                        obstacle.mandatory = True
                        mandEnd.remove((point, entry))
        if self.symmetrical:
            self.setMirrors()

    def connectAligned(self, obstacles):
        '''Checks any obstacles connected to others; if their gradients are
        identical, they will cease to exist, and become one long obstacle'''
        for obstacle in obstacles:
            testObstacle = obstacle
            while testObstacle.endConnect in obstacles:
                if testObstacle.gradient == testObstacle.endConnect.gradient:
                    testObstacle = self.mergeObstacles(testObstacle,\
                                                       testObstacle.endConnect)
                else:
                    testObstacle = testObstacle.endConnect

    def mergeObstacles(self, obstacle1, obstacle2, loop = True):
        '''Will merge the two given obstacles into the one entity'''
        print 'merging'
        start = obstacle1.startPt
        end = obstacle2.endPt
        startConnect = obstacle1.startConnect
        endConnect = obstacle2.endConnect
        if loop:
            try:
                self.removeObstacle(obstacle1)
                print 'delete1'
            except ValueError:
                pass
            try:
                self.removeObstacle(obstacle2)
                print 'delete2'
            except ValueError:
                pass
            if obstacle1.mirror != obstacle2 and \
               obstacle1.mirror and obstacle2.mirror:
                print 'merging mirror'
                self.mergeObstacles(obstacle1.mirror, obstacle2.mirror, False)
        mandatory = obstacle1.mandatory or obstacle2.mandatory
        gradient = obstacle1.gradient
        
        newObstacle = Obstacle(start, end, mandatory)
        newObstacle.startConnect = startConnect
        newObstacle.endConnect = endConnect
        if endConnect:
            endConnect.startConnect = newObstacle
            print 'endConnect'
        if startConnect:
            startConnect.endConnect = newObstacle
            print 'startConnect'
        newObstacle.gradient = gradient
        newObstacle.mirror = newObstacle
        self.obstacles.append(newObstacle)
        return newObstacle
                        
        
            
# Namespace for interpreting block layout files.
blockFileNamespace = {'ForwardInterfaceMapBlock': ForwardInterfaceMapBlock,
                      'BackwardInterfaceMapBlock': BackwardInterfaceMapBlock,
                      'TopBodyMapBlock': TopBodyMapBlock,
                      'BottomBodyMapBlock': BottomBodyMapBlock}


imgExt = '.png'
blockExt = '.block'

def run():
    main = MapBlockCreator()
    main.run()


if __name__ == '__main__':
    run()
