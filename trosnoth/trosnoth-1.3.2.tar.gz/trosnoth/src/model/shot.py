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

from trosnoth.src.model.unit import Unit
from trosnoth.src.model.map import MapLayout
from math import sin, cos, atan2, sqrt

from trosnoth.src.utils import logging
from trosnoth.src.utils.checkpoint import checkpoint



class GrenadeShot(Unit):
    '''This will make the grenade have the same physics as a player without control
    and features of player movement'''

    # The following values control grenade movement.
    maxFallVel = 540            # pix/s
    gravity = 1000 #3672              # pix/s/s
    initYVel = -400
    initXVel = 200

    def __init__(self, universe, player, id):
        Unit.__init__(self)
        self.universe = universe
        self.player = player
        self.id = id
        self.local = False
        self.registeredHit = False
        
        # Place myself.
        self.pos = player.pos
        self.yVel = self.initYVel


        # Select x velocity
        if player._faceRight:
            self.xVel = self.initXVel
        else:
            self.xVel = -self.initXVel

        universe.addGrenade(self)

        try:
            self.currentMapBlock = player.currentMapBlock
            self.currentMapBlock.addGrenade(self)
        except IndexError:
            logging.writeException()
            print "Init: Grenade off map"
            self.kill()
            return
        checkpoint('Grenade created')

    def delete(self):
        self.universe.removeGrenade(self)

    def solid(self):
        return True
    
    def setMapBlock(self, block):
        self.currentMapBlock.removeGrenade(self)
        Unit.setMapBlock(self, block)
        block.addGrenade(self)
              
    
    def update(self, deltaT):
        '''Called by this player's universe when this player should update
        its position. deltaT is the time that's passed since its state was
        current, measured in seconds.'''

        try:
            deltaX = self.xVel * deltaT
            deltaY = self.yVel * deltaT
            
            while True:
                # Check for collisions with solid objects, and change of zone.

                obstacle = self.currentMapBlock.moveUnit(self, deltaX, deltaY)

                
                if obstacle:

                    # Ask obstacle where the player should end up.
                    targetPt = obstacle.finalPosition(self.pos, deltaX, deltaY)
                    
                    if targetPt == None:
                        break

                    deltaX = targetPt[0] - self.pos[0]
                    deltaY = targetPt[1] - self.pos[1]
                    
                else:
                    break


            if obstacle:
                # Hit an obstacle. Process change to velocity etc.
                if obstacle:
                   self.yVel = -self.yVel

            
            # v = u + at
            vFinal = self.yVel + self.gravity * deltaT
            if vFinal > self.maxFallVel:
                # Hit terminal velocity. Fall has two sections.
                deltaY = deltaY + (self.maxFallVel**2 - self.yVel**2) \
                         / (2 * self.gravity) + self.maxFallVel * (deltaT - \
                         (self.maxFallVel - self.yVel) / self.gravity)
                self.yVel = self.maxFallVel
            else:
                # Simple case: s=ut+0.5at**2
                deltaY = deltaY + self.yVel * deltaT + 0.5 * self.gravity * \
                         deltaT ** 2
                self.yVel = vFinal
        
        except:
            logging.writeException()


class Shot(Unit):
    
    NORMAL = 'normal'
    TURRET = 'turret'
    RICOCHET = 'ricochet'

    # Speed that shots travel at.
    SPEED = 600       # pix/s
    LIFETIME = 1.     # s
    
    def __init__(self, world, id, team, player, pos, velocity, kind, lifetime,
            mapBlock):
        Unit.__init__(self)

        self.world = world
        self.id = id
        self.team = team
        self.pos = tuple(pos)
        self.originatingPlayer = player
        self.vel = tuple(velocity)
        self.timeLeft = lifetime
        self.kind = kind
        self.currentMapBlock = mapBlock

        checkpoint('Shot created')

    def solid(self):
        return self.kind != Shot.TURRET
    
    def update(self, deltaT):
        '''Called by the universe when this shot should update its position.
        deltaT is the time that's passed since its state was current, measured
        in seconds.'''
        # Shots have a finite lifetime.
        self.timeLeft = self.timeLeft - deltaT
        if self.timeLeft <= 0:
            self.world.shotExpired(self)
            return

        # Remember where the shot was - this is so that collisions with path
        # of shot work.
        self.oldPos = self.pos
        
        delta = (self.vel[0]*deltaT,
                 self.vel[1]*deltaT)
        if True: #try:
            obstacle = self.currentMapBlock.moveUnit(self, *delta)
            if obstacle is not None:
                # Shot hit an obstacle.
                if self.kind == Shot.RICOCHET:
                    obsAngle = atan2(obstacle.deltaPt[1], obstacle.deltaPt[0])
                    shotAngle = atan2(delta[1], delta[0])
                    dif=shotAngle -obsAngle
                    final = obsAngle - dif
                    speed = sqrt(self.vel[0]*self.vel[0] + self.vel[1]*self.vel[1])
                    self.vel = (speed*cos(final), speed*sin(final))
                else:
                    self.world.shotExpired(self)
                    return
#        except AttributeError:
#            print "Update: Shot off map"
#            print MapLayout.getMapBlockIndices(self.pos[0], self.pos[1])
#            self.world.shotExpired(self)

