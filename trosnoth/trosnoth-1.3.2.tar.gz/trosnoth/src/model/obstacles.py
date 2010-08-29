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

'obstacle types'

from math import atan2, sin, cos

class Obstacle(object):
    '''Represents an obstacle which can't be passed by player or shot.'''
    __slots__ = ['pt1', 'deltaPt']
    epsilon = 1e-10

    def __init__(self, pt1, deltaPt):
        self.pt1 = pt1
        self.deltaPt = deltaPt

    @property
    def pt2(self):
        return (self.pt1[0] + self.deltaPt[0],
                self.pt1[1] + self.deltaPt[1])

    def collide(self, pt, deltaX, deltaY, soft=False):
        '''Returns how far a point-sized object at the specified position
        could travel if it were trying to travel a displacement of
        [deltaX, deltaY].
        If soft is true, there's less tolerance for rounding errors around
        corners, making it harder to hit the corners of the obstacle.
        '''
        if soft:
            epsilon = 0
        else:
            epsilon = 1e-10

        ax, ay = self.pt1
        bx, by = pt
        dX1, dY1 = self.deltaPt

        # Check if the lines are parallel.
        denom = dX1*deltaY - deltaX*dY1
        if denom <= epsilon:
            # We can go through it in this direction.
            return deltaX, deltaY

        # Calculate whether the line segments intersect.

        s = (deltaX * (ay-by) - deltaY * (ax-bx)) / denom
        # Take into account floating point error.
        if s <= -epsilon or s >= (1.+epsilon):
            return deltaX, deltaY

        t = (dX1 * (ay-by) - dY1 * (ax-bx)) / denom
        if t < -self.epsilon or t > (1.+self.epsilon):
            return deltaX, deltaY

        # Calculate the actual collision point.
        x = bx + t*deltaX
        y = by + t*deltaY

        # Return the allowed change in position.
        return x - pt[0], y - pt[1]

    def finalPosition(self, pt, deltaX, deltaY):
        '''Returns the final position of a point-sized object at the specified
        position which is attempting to travel along the given displacement.
        May assume that the object hits this obstacle on the way.
        If the final position is simply the collision point, should return
        None.'''
        return None

class JumpableObstacle(Obstacle):
    '''Represents an obstacle that is not a wall.'''

    def hitByPlayer(self, player):
        '''This obstacle has been hit by player.'''
        if player.bounce:
            player._jumpTime = player.maxJumpTime
            player.yVel = -player.yVel
            player._onGround = None
        else:
            player._jumpTime = 0
            player.yVel = 0

class GroundObstacle(JumpableObstacle):
    '''Represents an obstacle that players are allowed to walk on.'''
    drop = False
    def __init__(self, pt1, deltaPt):
        super(GroundObstacle, self).__init__(pt1, deltaPt)
        angle = atan2((deltaPt[1] + 0.), (deltaPt[0] + 0.))
        self.ratio = (cos(angle), sin(angle))
        self.leftGround = None
        self.rightGround = None
    def walkTrajectory(self, vel, deltaTime):
        '''Returns the displacement that a player would be going on this
        surface if they would travel, given an absolute velocity and an amount
        of time.'''
        return tuple([vel * deltaTime * self.ratio[i] for i in (0,1)])

    def inBounds(self, pos):
        '''Checks whether a given point is within the boundaries of this
        obstacle. Should be called by a player object who was on this piece
        of ground, and has just moved.'''
        return self.pt1[0] <= pos[0] <= self.pt1[0] + self.deltaPt[0]

    def checkBounds(self, pos):
        if pos[0] < self.pt1[0]:
            if self.leftGround is None:
                return None, pos
            return self.leftGround, self.pt1
        elif pos[0] > self.pt1[0] + self.deltaPt[0]:
            if self.rightGround is None:
                return None, pos
            return self.rightGround, (self.pt1[0] + self.deltaPt[0],
                                      self.pt1[1] + self.deltaPt[1])
        return self, pos

    def finalPosition(self, pt, deltaX, deltaY):
        '''Returns the final position of a point-sized object at the specified
        position trying to travel a displacement of [deltaX, deltaY], given
        that it collides with this obstacle.
        This routine takes into account that if the object is travelling
        upwards, it may slide up the obstacle. Returns None if no sliding is
        going on, to indicate that the object hits the ground.'''

        if deltaY > -0.001 or self.deltaPt[1] == 0:
            return None

        # We collided with the floor while jumping.

        # Go to the y position we would have gone to.
        y = pt[1] + deltaY

        # Calculate where this lies on the floor slope.
        x = self.pt1[0] + (y - self.pt1[1]) * (self.deltaPt[0] /
                (self.deltaPt[1] + 0.))

        return x, y

class LedgeObstacle(GroundObstacle):
    drop = True

class RoofObstacle(Obstacle):
    def __init__(self, pt1, deltaPt):
        super(RoofObstacle, self).__init__(pt1, deltaPt)

    def finalPosition(self, pt, deltaX, deltaY):
        '''Returns the final position of a point-sized object at the specified
        position trying to travel a displacement of [deltaX, deltaY], given
        that it collides with this obstacle.'''
        # If an object collides with a roof obstacle while falling, it still
        #  falls.

        if deltaY > 0:
            # We collided with the roof while falling.
            # New position is where the roof is at the correct y-position.

            # These next few lines are just here to make sure that there's not
            # a divide by zero error:
            if deltaX == 0 or self.deltaPt[1] == 0:
                return None
            # I added a quick fix to the bug that causes an infinite loop
            # while players are touching a sloped roof, by adding 0.1 to
            # the player's position, in the direction opposite travel. Have
            # not been able to reproduce the bug since, however should be
            # looked at some more. -Ashley (Smashery)
            x = self.pt1[0] + (pt[1] + deltaY - self.pt1[1]) * \
                 self.deltaPt[0] / (0. + self.deltaPt[1]) - \
                 ((deltaX / abs(deltaX)) * 0.1)
            y = pt[1] + deltaY
            # Note: the above statement should only ever cause a division by
            #  zero if someone has been silly enough to put a piece of
            #  horizontal roof in upside down (impassable from above not below)
            return x, y

        # Normal case:
        return None

    def hitByPlayer(self, player):
        # Stop any upward motion of the player.
        player.yVel = max(player.yVel, 0)
        player._jumpTime = 0

class FillerRoofObstacle(RoofObstacle):
    '''Represents an obstacle that would be used as an obstacleEdge;
    its endpoint calculations are less precise (that being they
    don't exist), but are able to be so due to their usage.'''

    def finalPosition(self, pt, deltaX, deltaY):
        if self.deltaPt[0] == 0:
            return pt[0], pt[1] + (deltaY/2)
        else:
            super(FillerRoofObstacle, self).finalPosition(pt, deltaX, deltaY)

    def collide(self, pt, deltaX, deltaY, soft=True):
        '''Returns how far a point-sized object at the specified position
        could travel if it were trying to travel a displacement of
        [deltaX, deltaY].
        '''
        # Note: This routine is deliberately slightly different to the default
        # collide() in that it has less tolerance for rounding error around
        # corners. this is deliberate.
        return super(FillerRoofObstacle, self).collide(pt, deltaX, deltaY,
                soft=True)

class VerticalWall(JumpableObstacle):
    '''Represents a vertical wall that players can cling to and climb.'''
    drop = True

    def __init__(self, pt1, deltaPt):
        assert deltaPt[0] == 0

        # Can drop off a vertical wall, so drop is always set to True
        super(VerticalWall, self).__init__(pt1, deltaPt)

    def unstickyWallFinalPosition(self, pt, deltaX, deltaY):
        '''Returns the final position of a point-sized object at the specified
        position trying to travel a displacement of [deltaX, deltaY], given
        that it collides with this obstacle.'''
        # If an object collides with a roof obstacle while falling, it still
        #  falls.

        if deltaY == 0:
            return None

        return pt[0], pt[1] + deltaY
