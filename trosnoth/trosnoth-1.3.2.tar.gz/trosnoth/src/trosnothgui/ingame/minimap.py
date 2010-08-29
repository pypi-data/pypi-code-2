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

'''miniMap.py - defines the MiniMap class which deals with drawing the
miniMap to the screen.'''

import random
import pygame
from trosnoth.src.trosnothgui.ingame.sprites import PlayerSprite
from trosnoth.src.model.map import MapLayout
from trosnoth.src.model import mapblocks
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.framework.basics import Animation

# TODO: Get a full-screen minimap upon a hotkey.

class MiniMap(framework.Element):

    def __init__(self, app, scale, universe, viewManager):
        '''Called upon creation of a ViewManager object.  screen is a pygame
        screen object.  universe is the Universe object to draw.  target is
        either a point, a Player object, or None.  If target is None, the view
        manager will follow the action, otherwise it will follow the specified
        point or player.'''
        super(MiniMap, self).__init__(app)
        self.scale = scale
        self.universe = universe
        self.viewManager = viewManager
        self.disrupt = False
        # Initialise the graphics in all the mapBlocks
        bodyBlockSize = (MapLayout.zoneBodyWidth / scale,
                              MapLayout.halfZoneHeight / scale)
        self.bodyBlockRect = pygame.Rect((0,0), bodyBlockSize)

        interfaceBlockSize = (MapLayout.zoneInterfaceWidth /scale,
                              MapLayout.halfZoneHeight / scale)
        self.interfaceBlockRect = pygame.Rect((0,0), interfaceBlockSize)
        self.disruptAnimation = self.createDisrupted()
        # self._focus represents the point where the miniMap is currently
        # looking.
        self._focus = None
        self.updateFocus()

    def getScaledMaximumSize(self):
        # 35% of screen size
        # TODO: higher if on a fullscreen larger than game size
        return tuple([self.app.screenManager.scaledSize[i] * 35 / 100 for i in 0,1])

    def getAbsoluteMaximumSize(self):
        # Could be aptly described as the minumum maximum
        return (300,200)

    def getMaximumSize(self):
        size1 = self.getScaledMaximumSize()
        size2 = self.getAbsoluteMaximumSize()
        return tuple([max(size1[i], size2[i]) for i in 0,1])

    def getUniverseScaledSize(self):
        universeSize = len(self.universe.zoneBlocks[0]), len(self.universe.zoneBlocks)

        mapHeight = universeSize[1] * self.bodyBlockRect.height
        mapWidth = (universeSize[0] / 2) * self.bodyBlockRect.height + \
                   (universeSize[0] / 2 + 1) * self.interfaceBlockRect.width

        return (mapWidth, mapHeight)

    def getSize(self):
        size1 = self.getUniverseScaledSize()
        size2 = self.getMaximumSize()
        return tuple([min(size1[i], size2[i]) for i in 0,1])

    def getOffset(self):
        return self.app.screenManager.size[0] - self.getSize()[0] - 5, 5

    def getRect(self):
        return pygame.Rect(self.getOffset(), self.getSize())

    def createDisrupted(self):
        # TODO: Callthis again if the size changes
        screens = []
        sRect = self.getRect()
        for a in range(0,4):
            screen = (pygame.surface.Surface(sRect.size))
            x = y = yy = 0
            rect = pygame.rect.Rect(0,0,2,2)
            disruptColours = disruptColours = [self.app.theme.colours.minimapDisruptionColour1, self.app.theme.colours.minimapDisruptionColour2]
            
            while x < sRect.right:
                while y < sRect.bottom:
                    rect.top = y
                    pygame.draw.rect(screen, random.choice(disruptColours), rect, 0)
                    y += 2
                y = yy
                rect.left = x
                x += 2
            screens.append(screen)
        return Animation(0.1, *screens)
    
    def drawDisrupted(self, screen):
        screen.blit(self.disruptAnimation.getImage(), self.getOffset())
        
    def draw(self, screen):
        '''Draws the current state of the universe at the current viewing
        location on the screen.  Does not call pygame.display.flip() .'''

        colours = self.app.theme.colours
        sRect = self.getRect()
        pygame.draw.rect(screen, colours.black, sRect, 0)

        # If disrupted, draw static 95% of the time
        if self.disrupt and random.random() > 0.05:
            self.drawDisrupted(screen)
        else:
            # Update where we're looking at.
            self.updateFocus()

            self.drawZones(screen)

            # DRAW PLAYERS

            # Go through and update the positions of the players on the screen.
            for player in self.universe.players:
                # Calculate the position of the player.
                playerPos = [(player.pos[i] - self._focus[i]) / self.scale + \
                                      sRect.center[i] for i in (0,1)]
                if sRect.collidepoint(*playerPos):

                    # The player being drawn is the one controlled by the user.
                    if (hasattr(self.viewManager.target, 'player') and player ==
                            self.viewManager.target.player):
                        clr = colours.minimapOwnColour
                        radius = 3

                    else:
                        if player.ghost:
                            clr = self.app.theme.colours.miniMapGhostColour(
                                    player.team)
                        else:
                            clr = self.app.theme.colours.miniMapPlayerColour(
                                    player.team)
                        radius = 2
                    playerPos = [int(playerPos[i]) for i in (0,1)]
                    pygame.draw.circle(screen, clr, playerPos, radius)




            # Draw the shots.
            for shot in self.universe.shots:
                # Calculate the position of the player.
                shotPos = [(shot.pos[i] - self._focus[i]) / self.scale + \
                        sRect.center[i] for i in (0,1)]
                if sRect.collidepoint(*shotPos):
                    shotPos = [int(shotPos[i]) for i in (0,1)]
                    pygame.draw.circle(screen, colours.white, shotPos, 0)

        # Finally, draw the border
        pygame.draw.rect(screen, self.app.theme.colours.minimapBorder,
                sRect, 2)

    def drawZones(self, screen):
        '''Draws the miniMap graphics onto the screen'''
        # TODO: It's still a few pixels out on the bottom of the minimap
        sRect = self.getRect()
        topCorner = [self._focus[i] - (sRect.size[i] / 2 * self.scale) \
                     for i in (0,1)]
        # Find which map blocks are on the screen.
        i, j = MapLayout.getMapBlockIndices(*topCorner)
        i = max(0, i)
        j = max(0, j)
        firstBlock = self.universe.zoneBlocks[i][j]


        # Set the initial position back to where it should be.
        firstPos = [min((firstBlock.defn.rect.topleft[a] - topCorner[a]) / self.scale +\
                    sRect.topleft[a], sRect.topleft[a]) for a in (0,1)]

        posToDraw = [firstPos[a] for a in (0,1)]
        y, x = i, j
        while True:
            while True:
                try:
                    block = self.universe.zoneBlocks[y][x]
                except IndexError:
                    break
                if isinstance(block, mapblocks.InterfaceMapBlock):
                    currentRect = self.interfaceBlockRect
                else:
                    currentRect = self.bodyBlockRect
                currentRect.topleft = posToDraw
                area = currentRect.clip(sRect)
                if area.size == currentRect.size:
                    # Nothing has changed.
                    self._drawBlockMiniBg(block, screen, currentRect)
                elif area.size == (0,0):
                    # Outside the bounds of the minimap
                    pass
                else:
                    self._drawBlockMiniBg(block, screen, currentRect, area)

                posToDraw[0] += currentRect.width
                if posToDraw[0] > sRect.right:
                    break
                x += 1
            x = j
            y += 1
            # Next Row
            posToDraw[0] = firstPos[0]
            # Add the height; could use either bodyBlockRect or interfaceBlockRect; they
            # have the same height.
            posToDraw[1] += self.interfaceBlockRect.height
            if posToDraw[1] > sRect.bottom:
                break

    def _drawBlockMiniBg(self, block, surface, rect, area=None):
        if block.defn.kind == 'fwd':
            self._drawFwdBlockMiniBg(block, surface, rect, area)
        elif block.defn.kind == 'bck':
            self._drawBckBlockMiniBg(block, surface, rect, area)
        else:
            self._drawBodyBlockMiniBg(block, surface, rect, area)
        self._drawBlockMiniArtwork(block, surface, rect, area)

    def _drawBlockMiniArtwork(self, block, surface, rect, area):
        if block.defn.graphics is None:
            return

        if area is not None:
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(block.defn.graphics.getMini(self.scale), area.topleft, crop)
        else:
            surface.blit(block.defn.graphics.getMini(self.scale), rect.topleft)

    def _drawBodyBlockMiniBg(self, block, surface, rect, area):
        if block.zone:
            clr = self._getMiniMapColour(block.zone)
        else:
            clr = (0, 0, 0)
        if area is not None:
            pygame.draw.rect(surface, clr, area)
        else:
            pygame.draw.rect(surface, clr, rect)

    def _drawFwdBlockMiniBg(self, block, surface, rect, area):
        # TODO: implement as per drawBlock()
        if area:
            tempSurface = pygame.surface.Surface(rect.size)
            tempRect = tempSurface.get_rect()
        if block.zone1:
            clr = self._getMiniMapColour(block.zone1)
        else:
            clr = (0, 0, 0)
        if area:
            pts = (tempRect.topleft, tempRect.topright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
        else:
            pts = (rect.topleft, rect.topright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

        if block.zone2:
            clr = self._getMiniMapColour(block.zone2)
        else:
            clr = (0, 0, 0)

        if area:
            pts = (tempRect.bottomright, tempRect.topright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
            # Now put it onto surface
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(tempSurface, area.topleft, crop)
        else:
            pts = (rect.bottomright, rect.topright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

    def _drawBckBlockMiniBg(self, block, surface, rect, area):
        # TODO: implement it the same as drawBlock()
        if area:
            tempSurface = pygame.surface.Surface(rect.size)
            tempRect = tempSurface.get_rect()
        if block.zone1:
            clr = self._getMiniMapColour(block.zone1)
        else:
            clr = (0, 0, 0)

        if area:
            pts = (tempRect.topleft, tempRect.bottomright, tempRect.bottomleft)
            pygame.draw.polygon(tempSurface, clr, pts)
        else:
            pts = (rect.topleft, rect.bottomright, rect.bottomleft)
            pygame.draw.polygon(surface, clr, pts)

        if block.zone2:
            clr = self._getMiniMapColour(block.zone2)
        else:
            clr = (0, 0, 0)
        if area:
            pts = (tempRect.topleft, tempRect.bottomright, tempRect.topright)
            pygame.draw.polygon(tempSurface, clr, pts)
            # Now put it onto surface
            cropPos = (area.left - rect.left, area.top - rect.top)
            crop = pygame.rect.Rect(cropPos, area.size)
            surface.blit(tempSurface, area.topleft, crop)
        else:
            pts = (rect.topleft, rect.bottomright, rect.topright)
            pygame.draw.polygon(surface, clr, pts)

    def _getMiniMapColour(self, zone):
        colours = self.app.theme.colours
        if zone.zoneOwner:
            return colours.miniMapZoneOwnColour(zone.orbOwner)
        elif zone.orbOwner:
            return colours.miniMapOrbOwnColour(zone.orbOwner)
        else:
            return colours.neutral_mn_bg

    # The right-most and left-most positions at which the minimap can focus
    def getBoundaries(self):
            # The edge of the map will always be an interfaceMapBlock
        indices = (len(self.universe.zoneBlocks) - 1,
                   len(self.universe.zoneBlocks[0]) - 1)

        block = self.universe.zoneBlocks[indices[0]][indices[1]]
        pos = block.defn.rect.bottomright
        sRect = self.getRect()
        rightMost = (pos[0] - sRect.size[0] * self.scale / 2,
                             pos[1] - sRect.size[1] * self.scale / 2)

        # The left-most position at which the minimap can focus
        leftMost = (sRect.size[0] * self.scale / 2,
                            sRect.size[1] * self.scale / 2)

        return rightMost, leftMost

    def updateFocus(self):
        if isinstance(self.viewManager.target, PlayerSprite):
            self._focus = self.viewManager.target.pos
        elif self.viewManager.target == None:
            self._focus = self.viewManager._focus
        else:
            #assert isinstance(self._focus, tuple)
            self._focus = self.viewManager.target

        rightMost, leftMost = self.getBoundaries()
        self._focus = [max(min(self._focus[i], rightMost[i]),\
                           leftMost[i]) for i in (0,1)]

    def disrupted(self):
        self.disrupt = True

    def endDisruption(self):
        self.disrupt = False
