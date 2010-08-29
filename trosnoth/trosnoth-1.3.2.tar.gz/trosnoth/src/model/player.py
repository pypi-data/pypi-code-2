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

from math import sin, cos
import struct

import trosnoth.src.utils.logging as logging
from trosnoth.src.utils.checkpoint import checkpoint

#####

from trosnoth.src.model.unit import Unit
from trosnoth.src.model.obstacles import JumpableObstacle, VerticalWall, GroundObstacle
from trosnoth.src.model.map import MapLayout

from trosnoth.src.messages import (DeleteUpgradeMsg, PlayerUpdateMsg, PlayerKilledMsg)
from trosnoth.src.network.utils import compress_boolean
from trosnoth.src.utils.utils import timeNow

RESPAWN_CAMP_TIME = 1.0
MAX_STARS = 10

class Player(Unit):
    '''Maintains the state of a player. This could be the user's player, a
    player on the network, or conceivably even a bot.

    If this player is controlled locally (human or bot), then player.local
    is True. If the player is controlled by the network, player.local is False.
    '''

    STARS_TO_RESET_TO = 0    

    def __init__(self, universe, nick, team, id, zone, dead=False,
            local=True):
        '''Note that player instances are not local when they are created.
        The value of local is set only when the server gives us the player
        by calling self.makeLocal().'''
        Unit.__init__(self)

        self.universe = universe
        self.nick = nick
        self.team = team
        self.id = id
        self.local = local
        self._state = {'left':  False,
                       'right': False,
                       'jump':  False,
                       'down': False,
                       'respawn' : False}

        self.stars = self.STARS_TO_RESET_TO

        # Place myself.
        self.pos = zone.defn.pos
        self._jumpTime = 0.0
        self.yVel = 0
        self._onGround = None
        self._ignore = None                 # Used when dropping through a platform.
        self.angleFacing = 1.57
        self.ghostThrust = 1.0              # Determined by mouse position
        self._faceRight = True
        self._unstickyWall = None
        self.reloadTime = 0.0
        self.turretHeat = 0.0
        self.respawnGauge = 0.0
        self.upgradeGauge = 0.0
        self.upgradeTotal = 0.0
        self.health = self.respawnHealth
        self.ghost = dead
        # Upgrade-related
        self.upgrade = None
        self.shielded = False
        self.hasRicochet = False
        self.phaseshift = False
        self.turret = False
        self.turretOverHeated = False
        self.invulnerableUntil = None

        # Shots this player has fired
        self.shots = {}

        self.currentZone = zone
        zone.addPlayer(self)

    def isInvulnerable(self):
        iu = self.invulnerableUntil
        if iu is None:
            return False
        elif timeNow() > iu:
            self.invulnerableUntil = None
            return False
        return True

    def setPos(self, pos):
        self.pos = pos
        # Ensure we're in the right mapBlock
        i, j = MapLayout.getMapBlockIndices(*pos)
        self.currentMapBlock = self.universe.zoneBlocks[i][j]

        # TODO: try to put ourselves on solid ground.

    def __repr__(self):
        return self.nick

    def getDetails(self):

        pID = struct.unpack('B', self.id)[0]
        nick = self.nick
        team = self.team.id
        dead = self.ghost
        stars = self.stars
        if self.upgrade:
            upgrade = repr(self.upgrade)
            upgradeInUse = self.upgrade.inUse
        else:
            upgrade = None
            upgradeInUse = False

        return {'pID': pID,
                'nick': nick,
                'team': team,
                'dead': dead,
                'stars': stars,
                'upgrade': upgrade,
                'upgradeInUse': upgradeInUse}

    def removeFromGame(self):
        '''Called by network client when server says this player has left the
        game.'''
        # Remove myself from the register of players.
        self.team.playerHasLeft(self)
        if self.upgrade:
            self.upgrade.delete()

        # Remove myself from all groups I'm in.
        self.currentMapBlock.removePlayer(self)
        self.currentZone.removePlayer(self)

        # TODO: These lines would be nice, but for now shots are keyed by
        # player.
#        for sId, shot in self.shots.iteritems():
#            shot.originatingPlayer = None

    def makeLocal(self):
        'Called by network client at instruction of server.'
        self.local = True

    def solid(self):
        return not self.ghost

    def setMapBlock(self, block):
        self.currentMapBlock.removePlayer(self)
        Unit.setMapBlock(self, block)
        block.addPlayer(self)

        # If we're changing blocks, we can't hold on to the same obstacle,
        # as obstacles belong to a particular mapblock.
        self._onGround = None

    def updateState(self, key, value):
        '''Update the state of this player. State information is information
        which is needed to calculate the motion of the player. For a
        human-controlled player, this is essentially only which keys are
        pressed. Keys which define a player's state are: left, right, jump and
        down.
        Shooting is processed separately.'''

        if key in ('left', 'right'):
            self._unstickyWall = None

        # Ignore messages if we already know the answer.
        if self._state[key] == value:
            return
        if not self.ghost:
            # If a jump is requested and we're not on the ground, ignore it.
            if key == 'jump':
                if value:
                    if not self._onGround or not isinstance(self._onGround, \
                                                            JumpableObstacle):
                        return

                    # Otherwise, initiate the jump.
                    self._jumpTime = self.maxJumpTime
                    self._onGround = None
                elif self._jumpTime > 0:
                    # If we're jumping, cancel the jump.
                    # The following line ensures that small jumps are possible
                    #  while large jumps still curve.
                    self.yVel = -(1 - self._jumpTime / self.maxJumpTime) * \
                                self.jumpThrust
                    self._jumpTime = 0

        # Set the state.
        self._state[key] = value

    def lookAt(self, angle, thrust=None):
        '''Changes the direction that the player is looking.  angle is in
        radians and is measured clockwise from the right.'''
        if thrust is not None:
            self.ghostThrust = thrust

        if self.angleFacing == angle:
            return

        self.angleFacing = angle
        self._faceRight = angle > 0

    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''

        # Update upgrade gauge based on Time:
        if self.upgrade and self.upgradeGauge > 0:
            self.upgradeGauge -= deltaT
            if self.upgradeGauge <= 0:
                self.upgrade.timeIsUp()
                self.universe.eventPlug.send(DeleteUpgradeMsg(self.id, self.upgrade.upgradeType))

        #########
        # GHOST #
        #########
        if self.ghost:
            deltaX = self.maxGhostVel * deltaT * sin(self.angleFacing) * self.ghostThrust
            deltaY = -self.maxGhostVel * deltaT * cos(self.angleFacing) * self.ghostThrust

            self.currentMapBlock.moveUnit(self, deltaX, deltaY)

            # Update respawn gauge based on Time:
            if self.respawnGauge >= 0:
                self.respawnGauge -= deltaT

        ##########
        # TURRET #
        ##########
        elif self.turret:

            # Now adjust the time till reloaded.
            self.reloadTime = max(0.0, self.reloadTime - deltaT)

            self.turretHeat = max(0.0, self.turretHeat - deltaT)
            if self.turretOverHeated and self.turretHeat == 0.0:
                self.turretOverHeated = False


        ##########
        # PLAYER #
        ##########
        else:

            # Consider horizontal movement of player.
            if self._state['left'] and not self._state['right']:
                if self._faceRight:
                    absVel = -self.slowXVel
                else:
                    absVel = -self.xVel
            elif self._state['right'] and not self._state['left']:
                if self._faceRight:
                    absVel = self.xVel
                else:
                    absVel = self.slowXVel
            else:
                absVel = 0

            # Allow falling through fall-through-able obstacles
            if self._onGround and self._onGround.drop and self._state['down']:

                # Put the player through the floor:
                if not isinstance(self._onGround, VerticalWall):
                    checkpoint('Player: drop through ledge')
                    self._ignore = self._onGround
                else:
                    checkpoint('Player: drop off wall downwards')
                self._onGround = None

            # Now consider vertical movement.
            if isinstance(self._onGround, GroundObstacle):
                # Ask the ground obstacle I'm on where I'm moving to.
                deltaX, deltaY = self._onGround.walkTrajectory(absVel, deltaT)

                # Check for collisions in this path.
                self._move(deltaX, deltaY)
            elif isinstance(self._onGround, VerticalWall):
                # Stuck to the wall. Allow falling off:
                if self._state['right'] and self._onGround.deltaPt[1] > 0 \
                   or (self._state['left'] and self._onGround.deltaPt[1] < 0):
                    self._onGround = None
                    self.fallTime = deltaT
                    checkpoint('Player: drop off wall sideways')
            else:
                deltaY = 0
                deltaX = absVel * deltaT

                # If the player is jumping, calculate how much they jump by.
                if self._jumpTime > 0:
                    thrustTime = min(deltaT, self._jumpTime)
                    self.yVel = -self.jumpThrust
                    deltaY = thrustTime * self.yVel
                    self._jumpTime = self._jumpTime - deltaT

                    # Automatically switch off the jumping state if the player
                    # has reached maximum time.
                    if self._jumpTime <= 0:
                        self.updateState('jump', False)
                        self._jumpTime = 0
                    fallTime = deltaT - thrustTime
                else:
                    fallTime = deltaT

                # If player is falling, calculate how far they fall.

                # v = u + at
                vFinal = self.yVel + self.gravity * fallTime
                if vFinal > self.maxFallVel:
                    # Hit terminal velocity. Fall has two sections.
                    deltaY = deltaY + (self.maxFallVel**2 - self.yVel**2) \
                             / (2 * self.gravity) + self.maxFallVel * (fallTime - \
                             (self.maxFallVel - self.yVel) / self.gravity)
                    self.yVel = self.maxFallVel
                else:
                    # Simple case: s=ut+0.5at**2
                    deltaY = deltaY + self.yVel * fallTime + 0.5 * self.gravity * \
                             fallTime ** 2
                    self.yVel = vFinal

                # Check for collisions in this path.
                self._move(deltaX, deltaY)

            # Now adjust the time till reloaded.
            self.reloadTime = max(0.0, self.reloadTime - deltaT)

    def _move(self, deltaX, deltaY):
        '''Called by the player's update() routine to move the player a given
        distance. This method should check for collisions with bullets and the
        ground.'''

        lastObstacle = None
        for i in xrange(100):
            lastPosition = self.pos
            # Check for collisions with solid objects, and change of zone.
            obstacle = self.currentMapBlock.moveUnit(self, deltaX, deltaY)
            if obstacle is None:
                break
            if self.pos == lastPosition and obstacle == lastObstacle:
                print 'Apparently infinite motion loop.'
                print ' -> block pos %s' % (self.currentMapBlock.defn.indices,)
                print ' -> block kind %s' % (self.currentMapBlock.defn.kind,)
                print ' -> obstacle %s' % (obstacle,)
                print ' -> unsticky wall %s' % (self._unstickyWall,)
                break
            lastObstacle = obstacle

            # Ask obstacle where the player should end up.
            if obstacle is self._unstickyWall:
                targetPt = obstacle.unstickyWallFinalPosition(self.pos, deltaX,
                        deltaY)
            else:
                targetPt = obstacle.finalPosition(self.pos, deltaX, deltaY)

            if targetPt is None:
                break

            deltaX = targetPt[0] - self.pos[0]
            deltaY = targetPt[1] - self.pos[1]
        else:
            print 'Very very bad thing: motion loop did not terminate after 100 iterations'

        # The following if statement will perform calculations for setting
        #  the current obstacle if any of the following conditions are met:
        # (1) Player is not currently on the ground.
        # (2) Player is currently on the ground and has hit another obstacle.
        # (3) Player was on the ground but has walked off the end.
        if not isinstance(self._onGround, GroundObstacle) or obstacle:
            if isinstance(obstacle, JumpableObstacle):
                if isinstance(self._onGround, GroundObstacle) and \
                       isinstance(obstacle, VerticalWall):
                    # Running into a vertical wall while on the ground.
                    # Don't attach self to it.
                    pass
                elif obstacle == self._unstickyWall:
                    # Player just dropped off this wall, don't reattach.
                    pass
                else:
                    if isinstance(obstacle, VerticalWall):
                        self._unstickyWall = obstacle
                    self._onGround = obstacle
                    self.universe.playerIsDirty(self.id)
            else:
                self._onGround = None
            if obstacle:
                # Hit an obstacle. Process change to velocity etc.
                if obstacle:
                    obstacle.hitByPlayer(self)
                    self.universe.playerIsDirty(self.id)
        elif isinstance(self._onGround, GroundObstacle):
            self._onGround, self.pos = self._onGround.checkBounds(self.pos)

        # Check for zone tag.
        if self.currentZone.orbOwner != self.team and self.local:
            self.universe.checkTag(self)

        self._ignore = None

    def changeZone(self, newZone):
        try:
            self.currentZone.removePlayer(self)
        except:
            logging.writeException()
        newZone.addPlayer(self)
        self.currentZone = newZone

    def die(self):
        self.ghost = True
        self.health = 0
        self.respawnGauge = self.respawnTotal
        self._jumpTime = 0
        self._setStarsForDeath()
        checkpoint('Player: died')
        if self.upgrade is not None and self.upgrade.goneWhenDie():
            self.universe.eventPlug.send(DeleteUpgradeMsg(self.id, self.upgrade.upgradeType))

    def deathDetected(self, shooterId, shotId):
        self.universe.eventPlug.send(PlayerKilledMsg(self.id,
                    shooterId, shotId))

    def _setStarsForDeath(self):
        self.stars = self.STARS_TO_RESET_TO

    def respawn(self):
        self._onGround = None
        self.ghost = False
        self.health = self.respawnHealth
        self.invulnerableUntil = timeNow() + RESPAWN_CAMP_TIME
        self.respawnGauge = 0
        self.pos = self.currentZone.defn.pos
        i, j = MapLayout.getMapBlockIndices(self.pos[0], self.pos[1])
        try:
            self.currentMapBlock = self.universe.zoneBlocks[i][j]
        except IndexError:
            raise IndexError, "You're off the map!"
        checkpoint('Player: respawned')

    def deleteUpgrade(self):
        '''Deletes the current upgrade object from this player'''
        if self.upgrade:
            print "%s's Upgrade Gone" % self.nick
            self.upgrade.delete()

    def destroyShot(self, sId):
        try:
            del self.shots[sId]
        except KeyError:
            pass

    def addShot(self, shot):
        self.shots[shot.id] = shot

    def incrementStars(self):
        if self.stars < MAX_STARS:
            self.stars += 1

    def getShotType(self):
        '''
        Returns one of the following:
            None - if the player cannot currently shoot
            'N' - if the player can shoot normal shots
            'R' - if the player can shoot ricochet shots
            'T' - if the player can shoot turret shots
        '''
        if self.ghost or self.phaseshift:
            return None

        # While on a vertical wall, one canst not fire
        if self.reloadTime > 0 or (self._onGround and
                isinstance(self._onGround, VerticalWall)):
            return None

        if self.hasRicochet:
            return 'R'
        if self.turret:
            if self.turretOverHeated:
                return None
            return 'T'
        return 'N'
    
    def makePlayerUpdate(self):
        values = compress_boolean((self._state['left'],
                self._state['right'], self._state['jump'],
                self._state['down'], self.upgrade is not None, self.ghost
                ))

        return PlayerUpdateMsg(self.id, self.pos[0],
                self.pos[1], self.yVel, self.angleFacing,
                self.ghostThrust, str(values))
