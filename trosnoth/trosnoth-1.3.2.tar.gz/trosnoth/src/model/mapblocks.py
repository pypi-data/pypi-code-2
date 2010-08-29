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
from trosnoth.src.model.obstacles import (GroundObstacle, LedgeObstacle,
        VerticalWall, FillerRoofObstacle, RoofObstacle)
from trosnoth.src.model.map import MapLayout
from trosnoth.src.model.universe_base import GameState

from trosnoth.src.messages import (DeleteUpgradeMsg,
        PlayerHitMsg, KillShotMsg)

# TODO: Don't use isinstance so we don't have to use this
from trosnoth.src.model.shot import Shot, GrenadeShot
from trosnoth.src.model.player import Player
from trosnoth.src.model.universe import Universe

class MapBlockDef(object):
    '''Represents the static information about a particular map block. A map
    block is a grid square, and may contain a single zone, or the interface
    between two zones.'''

    def __init__(self, kind, x, y):
        self.pos = (x, y)       # Pos is the top-left corner of this block.
        assert kind in ('top', 'btm', 'fwd', 'bck')
        self.kind = kind
        self.layout = None

        self.plObstacles = []   # Obstacles for players.
        self.shObstacles = []   # Obstacles for shots.
        self.indices = MapLayout.getMapBlockIndices(x, y)

        self.rect = pygame.Rect(x, y, 0, 0)
        self.rect.size = (self._getWidth(), MapLayout.halfZoneHeight)

        self.graphics = None
        self.debugGraphics = None
        self.blocked = False    # There's a barrier somewhere depending on type.

        # For body block.
        self.zone = None

        # For interface block.
        self.zone1 = None
        self.zone2 = None

    def __str__(self):
        return 'Block @ %r' % (self.indices,)

    def _getWidth(self):
        if self.kind in ('top', 'btm'):
            return MapLayout.zoneBodyWidth
        else:
            return MapLayout.zoneInterfaceWidth

    def spawnState(self, universe, zoneWithDef):
        if self.kind == 'top':
            return TopBodyMapBlock(universe, self,
                zoneWithDef.get(self.zone, None))
        elif self.kind == 'btm':
            return BottomBodyMapBlock(universe, self,
                zoneWithDef.get(self.zone, None))
        elif self.kind == 'fwd':
            return ForwardInterfaceMapBlock(universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        elif self.kind == 'bck':
            return BackwardInterfaceMapBlock(universe, self,
                zoneWithDef.get(self.zone1, None),
                zoneWithDef.get(self.zone2, None))
        else:
            assert False

    def getZones(self):
        result = []
        for z in (self.zone, self.zone1, self.zone2):
            if z is not None:
                result.append(z)
        return result

    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns the zone def for the zone at the specified point, ASSUMING
        that the point is in fact within this map block.'''
        if self.kind == 'fwd':
            # Equation of interface line:
            #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
            #                        + halfZoneHeight
            deltaY = y - self.pos[1] - MapLayout.halfZoneHeight
            deltaX = x - self.pos[0]

            if deltaY * MapLayout.zoneInterfaceWidth > \
                   -MapLayout.halfZoneHeight * deltaX:
                return self.zone2
            return self.zone1
        elif self.kind == 'bck':
            # Equation of interface line:
            #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
            deltaY = y - self.pos[1]
            deltaX = x - self.pos[0]

            if deltaY * MapLayout.zoneInterfaceWidth > \
                   MapLayout.halfZoneHeight * deltaX:
                return self.zone1
            return self.zone2
        else:
            return self.zone

    def addPlatform(self, pos, dx, reverse):
        '''Adds a horizontal platform which can be dropped through to this
        block's list of obstacles.

        pos         The position of the obstacle's first point relative to the
                    top-left corner of this block, or relative to the top-right
                    corner if reverse is set to True.
        dx          The horizontal displacement from first point to the second
                    point of the obstacle. This value should always be positive.
        reverse     Determines whether the obstacle is defined in terms of the
                    top-left corner of this map block or the top-right corner.
        '''

        # Add the block's position offset.
        pt = [pos[0] + self.pos[0],
              pos[1] + self.pos[1]]
        if reverse:
            pt[0] += self.rect.width

        # Put the platform in.
        x, y = pt

        self._obstacleEdge(pt, 7, LedgeObstacle)
        self._obstacle(pt, (x+dx, y), 0, LedgeObstacle)
        self._obstacleEdge((x+dx, y), 0, LedgeObstacle)

    def addObstacle(self, points, reverse):
        '''Adds an obstacle to this block's list of obstacles.

        points      A sequence specifying the positions of the obstacle's points
                    relative to the top-left corner of this block, or relative
                    to the top-right corner if reverse is set to True.
        reverse     Determines whether the obstacle is defined in terms of the
                    top-left corner of this map block or the top-right corner.
        '''

        # Go through and interpret list of points.
        # curPt - the point about which the next obstacle will start.
        # nextPt - the point about which the next obstacle will end.
        # cuCnr - the corner of the current point about from which the
        #           next line segment should start. Corners are represented
        #           as a number from 0 to 7, starting at zero as vertically
        #           above the point, and proceding in a clockwise direction.
        
        iterPoints = iter(points)
        nextPt = iterPoints.next()
        nextPt = [nextPt[0] + self.pos[0],
                  nextPt[1] + self.pos[1]]
        if reverse:
            nextPt[0] += self.rect.width
        curCnr = None

        while True:
            # Get next point.
            curPt = nextPt
            try:
                nextPt = iterPoints.next()
            except StopIteration:
                break

            # Add the block's position offset.
            nextPt = [nextPt[i] + self.pos[i] for i in (0,1)]
            if reverse:
                nextPt[0] += self.rect.width

            # Decide what corner it needs.
            dx, dy = (nextPt[i] - curPt[i] for i in (0, 1))
            if dx > 0:
                if dy < 0:      cnr = 7
                elif dy == 0:   cnr = 0
                else:           cnr = 1
            elif dx == 0:
                if dy > 0:      cnr = 2
                else:           cnr = 6
            else:
                if dy > 0:      cnr = 3
                elif dy == 0:   cnr = 4
                else:           cnr = 5

            if not curCnr:
                # First point: gets a bit of extra border.
                if cnr % 2:
                    curCnr = (cnr - 1) % 8
                else:
                    curCnr = (cnr - 2) % 8
                
            # Advance around current point until we reach the right corner.
            while curCnr != cnr:
                self._obstacleEdge(curPt, curCnr)
                curCnr = (curCnr + 1) % 8

            # Insert the correct line segment.
            self._obstacle(curPt, nextPt, curCnr)

        # Last point also gets a bit of extra border.
        if cnr % 2:
            cnr = (cnr + 1) % 8
        else:
            cnr = (cnr + 2) % 8
        while curCnr != cnr:
            self._obstacleEdge(nextPt, curCnr)
            curCnr = (curCnr + 1) % 8
        
    def coalesceLayout(self):
        '''
        Called once after all obstacles are added to the block. Used to
        connect ground obstacles so the player can walk between them.
        '''
        leftCorners = {}    # (x, y) -> obstacle
        rightCorners = {}    # (x, y) -> obstacle
        toRemove = set()
        for obstacle in self.plObstacles:
            if not isinstance(obstacle, GroundObstacle):
                continue
            left = obstacle.pt1
            right = obstacle.pt2
            if left in leftCorners:
                other = leftCorners[left]
                if obstacle.ratio[1] < other.ratio[1]:
                    leftCorners[left] = obstacle
                elif obstacle.ratio[1] == other.ratio[1]:
                    if obstacle.deltaPt[0] >= other.deltaPt[0]:
                        toRemove.add(other)
                        leftCorners[left] = obstacle
                        if rightCorners[other.pt2] == other:
                            del rightCorners[other.pt2]
                    else:
                        toRemove.add(obstacle)
                        continue
            else:
                leftCorners[left] = obstacle
            if right in rightCorners:
                other = rightCorners[right]
                if obstacle.ratio[1] > other.ratio[1]:
                    rightCorners[right] = obstacle
                elif obstacle.ratio[1] == other.ratio[1]:
                    if obstacle.deltaPt[0] >= other.deltaPt[0]:
                        toRemove.add(other)
                        rightCorners[right] = obstacle
                        if leftCorners[other.pt1] == other:
                            del leftCorners[other.pt1]
                    else:
                        toRemove.add(obstacle)
                        if leftCorners[obstacle.pt1] == obstacle:
                            del leftCorners[obstacle.pt1]
                        continue
            else:
                rightCorners[right] = obstacle

        for obstacle in list(self.plObstacles):
            if obstacle in toRemove:
                self.plObstacles.remove(obstacle)
                continue
            if not isinstance(obstacle, GroundObstacle):
                continue
            obstacle.leftGround = rightCorners.get(obstacle.pt1)
            obstacle.rightGround = leftCorners.get(obstacle.pt2)

    def _obstacle(self, pt0, pt1, cnr, kind=None):
        '''(kind, pt, delta) - internal. Adds a barrier for shots and players.
        kind        the class of obstacle to add for players.
        pt          the point about which the obstacle starts.
        offset      multipliers for offset to add to point.
        data        displacement from starting point.'''

        x,y = pt0
        delta = tuple(pt1[i] - pt0[i] for i in (0,1))
        kind2, offset, dummy, dummy = _cornerInfo[cnr]
        if kind == None:
            kind = kind2

        ox, oy = (offset[i] * Universe.halfPlayerSize[i] for i in (0,1))
        self.plObstacles.append(kind((x+ox, y+oy), delta))
        # Shots shouldn't worry about ledgeObstacles
        if kind == LedgeObstacle:
            pass
        else:
            ox, oy = (offset[i] * Universe.halfShotSize[i] for i in (0,1))
            self.shObstacles.append(kind((x+ox, y+oy), delta))

    def _obstacleEdge(self, pt, cnr, kind=None):
        '''(pt, cnr) - internal. Adds an edge barrier for players and shots
        around the specified point.
        '''
        if kind != LedgeObstacle:
            x,y = pt
            dummy, offset, kind2, deltaOffset = _cornerInfo[cnr]
            if kind == None:
                kind = kind2

            ox, oy = (offset[i] * Universe.halfPlayerSize[i] for i in (0,1))
            delta = [deltaOffset[i] * Universe.halfPlayerSize[i] for i in (0,1)]
            self.plObstacles.append(kind((x+ox, y+oy), delta))
            ox, oy = (offset[i] * Universe.halfShotSize[i] for i in (0,1))
            delta = [deltaOffset[i] * Universe.halfShotSize[i] for i in (0,1)]
            self.shObstacles.append(kind((x+ox, y+oy), delta))
            

class MapBlock(object):
    '''Represents a grid square of the map which may contain a single zone,
    or the interface between two zones.
    '''

    def __init__(self, universe, defn):
        self.universe = universe
        self.defn = defn

        self.shots = set()
        self.players = set()
        self.grenades = set()

    def removePlayer(self, player):
        if player in self.players:
            self.players.remove(player)

    def addPlayer(self, player):
        self.players.add(player)

    def __contains__(self, point):
        '''Checks whether a given point is within this zone.'''
        return self.defn.rect.collidepoint(*point)

    def _getBlockLeft(self):
        i, j = self.defn.indices
        if j == 0:
            return None
        return self.universe.zoneBlocks[i][j-1]
    blockLeft = property(_getBlockLeft)

    def _getBlockRight(self):
        i, j = self.defn.indices
        if j >= len(self.universe.zoneBlocks[i]) - 1:
            return None
        return self.universe.zoneBlocks[i][j+1]
    blockRight = property(_getBlockRight)
    
    def _getBlockAbove(self):
        i, j = self.defn.indices
        if i == 0:
            return None
        return self.universe.zoneBlocks[i-1][j]
    blockAbove = property(_getBlockAbove)

    def _getBlockBelow(self):
        i, j = self.defn.indices
        if i >= len(self.universe.zoneBlocks) - 1:
            return None
        return self.universe.zoneBlocks[i+1][j]
    blockBelow = property(_getBlockBelow)

    def getObstacles(self, unitClass):
        if issubclass(unitClass, Player):
            result = list(self.defn.plObstacles)

            return result
        if issubclass(unitClass, (Shot, GrenadeShot)):
            return self.defn.shObstacles
        return


    def getZoneAtPoint(self, x, y):
        '''getZoneAtPoint(x, y)
        Returns what zone is at the specified point, ASSUMING that the point
        is in fact within this map block.'''
        raise NotImplementedError, 'getZoneAtPoint not implemented.'

    def checkShotCollisions(self, player, deltaX, deltaY):
        '''Check for collisions of a local player with shots'''
        for shot in list(self.shots):
            if shot.team != player.team:
                if self.collideTrajectory(shot.pos, player.pos,
                                          (deltaX, deltaY), 20):
                    self.shotHitPlayer(shot, player)

    def checkPlayerCollisions(self, shot, deltaX, deltaY):
        '''Check for collisions of the specified shot with living local
        players. DeltaX and deltaY specify the path along which the shot is
        traveling.'''
        for player in self.players:
            if shot.team != player.team:
                # FIXME: It would be better not to have a hard-coded 20.
                if self.collideTrajectory(player.pos, shot.pos,
                                          (deltaX, deltaY), 20):
                    self.shotHitPlayer(shot, player)

    def shotHitPlayer(self, shot, player):
        if shot.registeredHit:
            return
        if shot.originatingPlayer is not None:
            shooterId = shot.originatingPlayer.id
        else:
            shooterId = '\x00'

        if player.ghost or player.turret or player.isInvulnerable():
            return
            
        shot.registeredHit = True
        if player.phaseshift:
            self.universe.eventPlug.send(KillShotMsg(shooterId, shot.id))
        elif player.shielded and player.upgrade.protections <= 1:
            self.universe.eventPlug.send(KillShotMsg(shooterId, shot.id))
            self.universe.eventPlug.send(DeleteUpgradeMsg(player.id, player.upgrade.upgradeType))
        elif player.health <= 1:
            player.deathDetected(shooterId, shot.id)
        else:
            self.universe.eventPlug.send(PlayerHitMsg(player.id, shooterId,
                    shot.id))

    def collideTrajectory(self, pt, origin, trajectory, tolerance):
        '''Returns true if pt lies within a distance of tolerance from the
        line segment described by origin and trajectory.'''

        # Get distance between point and trajectory origin.
        tr0 = origin
        d0 = ((tr0[0] - pt[0]) ** 2 + (tr0[1] - pt[1]) ** 2) ** 0.5
        if d0 < tolerance:
            return True

        delta = trajectory

        while True:
            # Calculate other end of trajectory.
            tr1 = (tr0[0] + delta[0],
                   tr0[1] + delta[1])
            d1 = ((tr1[0] - pt[0]) ** 2 + (tr1[1] - pt[1]) ** 2) ** 0.5

            # Check for collision.
            if d1 < tolerance:
                return True

            # Refine and loop.
            if d1 < d0:
                tr0, delta = tr1, (-0.5 * delta[0],
                                   -0.5 * delta[1])
            else:
                delta = (0.5 * delta[0],
                         0.5 * delta[1])

            # Check end condition.
            if (delta[0] ** 2 + delta[1] ** 2) < 5:
                return False
    
    def moveUnit(self, unit, deltaX, deltaY):
        '''moveUnit(unit, deltaX, deltaY)
        Attempts to move the unit by the specified amount, taking into
        account the positions of walls. Also checks if the unit
        changes zones or changes map blocks.

        If the unit is a player, checks for collisions with shots.
        If the unit hit an obstacle, returns the obstacle.
        This routine only checks for obstacle collisions if unit.solid() is
        True.
        Assumes that the unit is already within this map block.
        '''
        kind = unit.__class__
        
        lastObstacle = None
        if unit.solid():
            # Check for collisions with obstacles - find the closest obstacle.
            for obstacle in self.getObstacles(type(unit)):
                soft = False
                if kind == Player:
                    if unit._ignore == obstacle:
                        continue
                    elif (isinstance(unit._onGround, GroundObstacle) and
                            (obstacle == unit._onGround.leftGround or obstacle
                            == unit._onGround.rightGround)):
                        soft = True
                dX, dY = obstacle.collide(unit.pos, deltaX, deltaY, soft=soft)
                if (dX, dY) != (deltaX, deltaY):
                    # Remember the last obstacle we hit.
                    lastObstacle = obstacle
                    deltaX = dX
                    deltaY = dY

        # Check for change of map block.
        newBlock = False  # This is False because None means leaving the map.

        # Leaving via lefthand side.
        if deltaX < 0 and unit.pos[0] + deltaX < self.defn.pos[0]:
            # Check for collision with left-hand edge.
            y = unit.pos[1] + deltaY * (self.defn.pos[0] - unit.pos[0]) / deltaX
            if self.defn.rect.top <= y <= self.defn.rect.bottom:
                newBlock = self.blockLeft
        if newBlock == False and deltaX > 0 and unit.pos[0] + deltaX >= \
                                       self.defn.rect.right:
            # Check for collision with right-hand edge.
            y = unit.pos[1] + deltaY * (self.defn.rect.right - unit.pos[0]) \
                            / deltaX
            if self.defn.rect.top <= y <= self.defn.rect.bottom:
                newBlock = self.blockRight
        if newBlock == False and deltaY < 0 and unit.pos[1] + deltaY < self.defn.pos[1]:
            # Check for collision with top edge.
            x = unit.pos[0] + deltaX * (self.defn.pos[1] - unit.pos[1]) / deltaY
            if self.defn.rect.left <= x <= self.defn.rect.right:
                newBlock = self.blockAbove
        if newBlock == False and deltaY > 0 and unit.pos[1] + deltaY >= \
                                        self.defn.rect.bottom:
            x = unit.pos[0] + deltaX * (self.defn.rect.bottom - unit.pos[1]) \
                            / deltaY
            if self.defn.rect.left <= x <= self.defn.rect.right:
                newBlock = self.blockBelow
                
        universe = self.universe
        if newBlock == None and kind == Player:
            if not unit.ghost:
                # Player is off the map: mercy killing.
                unit.deathDetected('\x00', '\x00')
            return
        
        if newBlock:
            unit.setMapBlock(newBlock)
            if kind == Shot:
                self.removeShot(unit)
                newBlock.addShot(unit)
            
            # Another map block can handle the rest of this.
            return unit.currentMapBlock.moveUnit(unit, deltaX, deltaY)
        
        # Check for change of zones.
        if kind == Player:
            newZone = self.getZoneAtPoint(unit.pos[0] + deltaX,
                                          unit.pos[1] + deltaY)
            if (universe.gameState in (GameState.PreGame, GameState.Starting)
                    and newZone is None and unit.ghost):
                # Pre-game ghost cannot enter purple zones.
                return lastObstacle

            if newZone != unit.currentZone and newZone is not None:
                if universe.gameState in (GameState.PreGame,
                        GameState.Starting) and newZone.orbOwner != unit.team:
                    # Disallowed zone change.
                    return lastObstacle
                if not unit.local:
                    newZone = None
            else:
                newZone = None
        else:
            newZone = None

        # Check for player/shot collisions along the path.
        if kind == Player:
            if not unit.ghost:
                self.checkShotCollisions(unit, deltaX, deltaY)
        elif kind == Shot:
            self.checkPlayerCollisions(unit, deltaX, deltaY)
        
        # Move the unit.
        unit.pos = (unit.pos[0] + deltaX,
                      unit.pos[1] + deltaY)

        if newZone:
            # Zone needs to know which players are in it.
            unit.changeZone(newZone)

        return lastObstacle
            
    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        return

    def removeShot(self, shot):
        '''Removes a given shot from this mapBlock'''
        self.shots.remove(shot)

    def addShot(self, shot):
        '''Adds a given shot to this mapBlock'''
        if shot not in self.shots:
            self.shots.add(shot)

    def removeGrenade(self, grenade):
        '''Removes a given grenade from this mapBlock'''
        self.grenades.remove(grenade)

    def addGrenade(self, grenade):
        '''Adds a given grenade to this mapBlock'''
        self.grenades.add(grenade)
                
class BodyMapBlock(MapBlock):
    '''Represents a map block which contains only a single zone.'''

    def __init__(self, universe, defn, zone):
        super(BodyMapBlock, self).__init__(universe, defn)
        self.zone = zone

    def __str__(self):
        return '< %s >' % self.zone

    def getZoneAtPoint(self, x, y):
        return self.zone
    

class TopBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the top half of a zone.'''
    
    def orbPos(self, drawRect):
        return drawRect.midbottom

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''

        return min(abs(player.pos[1] - self.defn.rect.top), \
                   self.blockLeft.fromEdge(player),\
                   self.blockRight.fromEdge(player))

class BottomBodyMapBlock(BodyMapBlock):
    '''Represents a map block containing the bottom half of a zone.'''
    
    def orbPos(self, drawRect):
        return drawRect.midtop    

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is'''
        
        return min(abs(self.defn.rect.bottom - player.pos[1]), \
                   self.blockLeft.fromEdge(player),\
                   self.blockRight.fromEdge(player))

class InterfaceMapBlock(MapBlock):
    '''Base class for map blocks which contain the interface between two
    zones.'''

    def __init__(self, universe, defn, zone1, zone2):
        super(InterfaceMapBlock, self).__init__(universe, defn)

        self.zone1 = zone1
        self.zone2 = zone2
        
class ForwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a forward slash '/'.
    Note that exactly on the diagonal counts as being in the left-hand zone.
    '''

    def __str__(self):
        return '< %s / %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = -(halfZoneHeight / interfaceWidth)(x - self.x)
        #                        + halfZoneHeight
        deltaY = y - self.defn.pos[1] - MapLayout.halfZoneHeight
        deltaX = x - self.defn.pos[0]

        if deltaY * MapLayout.zoneInterfaceWidth > \
               -MapLayout.halfZoneHeight * deltaX:
            return self.zone2
        return self.zone1

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (self.defn.rect.left - player.pos[0], self.defn.rect.top - player.pos[1])
        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] + relPos[0] * \
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth + 384)
        # (where theta is the angle formed by the diagonal line seperating the
        # zones, and a vertical line).
        d = 0.8 * abs(relPos[1] + relPos[0] * 0.75 + 384)
        return d

class BackwardInterfaceMapBlock(InterfaceMapBlock):
    '''Represents a map block which contains the interface between two
    zones, split in the direction of a backslash '\'.
    Note that a point exactly on the diagonal counts as being in the left-hand
    zone.
    '''

    def __str__(self):
        return '< %s \ %s >' % (self.zone1, self.zone2)

    def getZoneAtPoint(self, x, y):
        # Equation of interface line:
        #   (y - self.y) = (halfZoneHeight / interfaceWidth)(x - self.x)
        deltaY = y - self.defn.pos[1]
        deltaX = x - self.defn.pos[0]

        if deltaY * MapLayout.zoneInterfaceWidth > \
               MapLayout.halfZoneHeight * deltaX:
            return self.zone1
        return self.zone2

    def fromEdge(self, player):
        '''Returns the distance from the edge of the zone that a player is.
        Assumes that the player is actually in this map block.'''
        relPos = (self.defn.rect.left - player.pos[0], self.defn.rect.top - player.pos[1])
        
        # Note: this following formula relies upon the dimensions:
        # MapLayout.halfZoneHeight = 384
        # MapLayout.zoneInterfaceWidth = 512
        # Should they be changed, should change this to:
        # d = sin(theta) * abs(relPos[1] - relPos[0] * \
        # MapLayout.halfZoneHeight / MapLayout.zoneInterfaceWidth)
        # where theta is the angle formed by the diagonal line seperating the
        # zones, and a vertical line.
        d = 0.8 * abs(relPos[1] - relPos[0] * 3 / 4)
        return d

            
        
# The following definition is used by the player class to add obstacles.
# Corner info: for each corner number (from 0 to 7), has a tuple of the
#            form (kind, offset, fillKind, fillDelta)
# kind          the kind of obstacle to use in _obstacle
# offset        the offset from the current point
# fillKind      the kind of obstacle to use for a filler from this point
# fillDelta     the change in offset for a filler from this corner
_cornerInfo = [(GroundObstacle, ( 0, -1), GroundObstacle,     ( 1,  0)),
               (GroundObstacle, ( 1, -1), FillerRoofObstacle, ( 0,  1)),
               (VerticalWall,   ( 1,  0), FillerRoofObstacle, ( 0,  1)),
               (RoofObstacle,   ( 1,  1), FillerRoofObstacle, (-1,  0)),
               (RoofObstacle,   ( 0,  1), FillerRoofObstacle, (-1,  0)),
               (RoofObstacle,   (-1,  1), FillerRoofObstacle, ( 0, -1)),
               (VerticalWall,   (-1,  0), FillerRoofObstacle, ( 0, -1)),
               (GroundObstacle, (-1, -1), GroundObstacle,     ( 1,  0))
               ]

