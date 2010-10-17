# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2010 Joshua D Bartlett
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

from math import pi
import random
from trosnoth.utils.components import Component, Plug, handler
from trosnoth.messages import (TaggingZoneMsg, ShootMsg, RespawnMsg,
        RespawnRequestMsg, PlayerKilledMsg, JoinRequestMsg, JoinSuccessfulMsg,
        CannotJoinMsg, UpdatePlayerStateMsg, AimPlayerAtMsg, RemovePlayerMsg,
        BuyUpgradeMsg)
from trosnoth.model.universe import Abort
from trosnoth.model.universe_base import GameState
from trosnoth.utils.math import distance
from math import atan2

from twisted.internet import reactor, task

class AIAgent(Component):
    '''
    Base class for an AI agent.
    '''
    eventPlug = Plug()
    requestPlug = Plug()
    aiPlug = Plug()

    def __init__(self, world, aiClass):
        Component.__init__(self)
        self.world = world
        self.aiClass = aiClass
        self.ai = None
        self.playerId = None
        self.team = None
        self._reqNicks = {}
        self._loop = task.LoopingCall(self._tick)

    def start(self, team=None):
        self.team = team
        self._loop.start(2)

    def stop(self):
        self._loop.stop()

    def _tick(self):
        if self.ai is not None:
            return
        if self.world.gameState != GameState.InProgress:
            return

        nick = self.aiClass.nick

        if self.team is None:
            teamId = '\x00'
        else:
            teamId = self.team.id

        reqTag = random.randrange(1<<32)
        self._joinGame(nick, teamId, reqTag, 1)

    def _joinGame(self, nick, teamId, reqTag, attempt):
        self._reqNicks[reqTag] = (nick, attempt)
        nick = '%s-%d' % (nick, attempt)
        self.requestPlug.send(JoinRequestMsg(teamId, reqTag, nick=nick.encode(),
                bot=True))
        return reqTag

    @handler(JoinSuccessfulMsg, eventPlug)
    def _joinSuccessful(self, msg):
        if msg.tag in self._reqNicks:
            del self._reqNicks[msg.tag]
        player = self.world.playerWithId[msg.playerId]
        self.ai = self.aiClass(self.world, player)
        self.playerId = player.id
        self.aiPlug.connectPlug(self.ai.plug)

    @handler(CannotJoinMsg, eventPlug)
    def _joinFailed(self, msg):
        r = msg.reasonId
        if msg.tag in self._reqNicks:
            nick, attempt = self._reqNicks.pop(msg.tag)
        else:
            nick = None

        if r == 'F':
            print 'Join failed for AI %r (full)' % (nick,)
        elif r == 'O':
            print 'Join failed for AI %r (game over)' % (nick,)
        elif r == 'W':
            print 'Join failed for AI %r (wait)' % (nick,)
        elif r == 'A':
            print 'Join failed for AI %r (not authenticated)' % (nick,)
        elif r == 'N':
            if nick is None:
                print 'Join failed for AI %r (nick)' % (self.aiClass.__name__,)
            else:
                attempt += 1
                self._joinGame(nick, msg.teamId, msg.tag, attempt)
        elif r == 'U':
            print 'Join failed for AI %r (user already in auth game)' % (nick,)
        else:
            print 'Join failed for AI %r (%r)' % (nick, r)

    @handler(RemovePlayerMsg, eventPlug)
    def _removePlayer(self, msg):
        if msg.playerId == self.playerId:
            self.ai.disable()
            self.ai = None
            self.playerId = None
            self.aiPlug.disconnectAll()

    @eventPlug.defaultHandler
    def gotEventMsg(self, msg):
        self.aiPlug.send(msg)

    @aiPlug.defaultHandler
    def gotAIMsg(self, msg):
        self.requestPlug.send(msg)

class AI(Component):
    plug = Plug()

    def __init__(self, world, player):
        Component.__init__(self)
        self.world = world
        self.player = player
        self.start()

    def start(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    @plug.defaultHandler
    def _ignoreMessage(self, msg):
        pass

    def doMoveRight(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='right'))
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='left'))

    def doMoveLeft(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='left'))
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='right'))

    def doStop(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='right'))
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='left'))

    def doDrop(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='down'))
        reactor.callLater(0.1, self._releaseDropKey)
    def _releaseDropKey(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='down'))

    def doJump(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, True,
                stateKey='jump'))

    def doStopJump(self):
        self.plug.send(UpdatePlayerStateMsg(self.player.id, False,
                stateKey='jump'))

    def doAimAt(self, angle, thrust=1.0):
        self.plug.send(AimPlayerAtMsg(self.player.id, angle, thrust))

    def doAimAtPoint(self, pos, thrust=1.0):
        x1, y1 = self.player.pos
        x2, y2 = pos
        angle = atan2(x2 - x1, -(y2 - y1))
        self.doAimAt(angle, thrust)

    def doShoot(self):
        self.plug.send(ShootMsg(self.player.id))

    def doRespawn(self):
        '''
        Attempts to respawn.
        '''
        self.plug.send(RespawnRequestMsg(self.player.id,
                random.randrange(1<<32)))

    def doBuyUpgrade(self, upgradeKind):
        '''
        Attempts to purchase an upgrade of the given kind.
        '''
        self.plug.send(BuyUpgradeMsg(self.player.id, upgradeKind.upgradeType,
                random.randrange(1<<32)))

    @handler(RespawnMsg, plug)
    def _respawned(self, msg):
        if msg.playerId == self.player.id:
            self.respawned()
    def respawned(self):
        pass

    @handler(PlayerKilledMsg, plug)
    def _playerKilled(self, msg):
        if msg.targetId == self.player.id:
            self.died(msg.killerId)
    def died(self, killerId):
        pass

    @handler(TaggingZoneMsg, plug)
    def _zoneTagged(self, msg):
        self.zoneTagged(msg.zoneId, msg.playerId)

    def zoneTagged(self, zoneId, playerId):
        pass

class SimpleAI(AI):
    '''
    An example of a simple AI which runs around randomly and shoots at the
    nearest enemy.
    '''
    nick = 'SimpleAI'

    def start(self):
        self._pauseTimer = None
        self._loop = task.LoopingCall(self.tick)
        self._loop.start(0.5)

    def disable(self):
        self._loop.stop()
        if self._pauseTimer is not None:
            self._pauseTimer.cancel()

    def tick(self):
        if self.player.dead:
            if self.player.inRespawnableZone():
                self.doAimAt(0, thrust=0)
                if self.player.respawnGauge == 0:
                    self.doRespawn()
            else:
                self.aimAtFriendlyZone()
        else:
            if self._pauseTimer is None:
                self.startPlayerMoving()
            if self.player.canShoot():
                self.fireAtNearestEnemy()

    def aimAtFriendlyZone(self):
        zones = [z for z in self.world.zones if z.orbOwner == self.player.team]
        if len(zones) == 0:
            return

        def getZoneDistance(zone):
            x1, y1 = self.player.pos
            x2, y2 = zone.defn.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        bestZone = min(zones, key=getZoneDistance)
        self.doAimAtPoint(bestZone.defn.pos)

    def fireAtNearestEnemy(self):
        enemies = [p for p in self.world.players if not
                (p.dead or self.player.isFriendsWith(p))]
        if len(enemies) == 0:
            return

        def getPlayerDistance(p):
            x1, y1 = self.player.pos
            x2, y2 = p.pos
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        nearestEnemy = min(enemies, key=getPlayerDistance)
        if getPlayerDistance(nearestEnemy) < 512:
            self.doAimAtPoint(nearestEnemy.pos)
            self.doShoot()

    def died(self, killerId):
        self._pauseTimer = None
        self.doStop()
        self.aimAtFriendlyZone()

    def respawned(self):
        self.startPlayerMoving()

    def startPlayerMoving(self):
        self.pauseAndReconsider()

    def pauseAndReconsider(self):
        if self.player.dead:
            self._pauseTimer = None
            return

        # Pause again in between 0.5 and 2.5 seconds time.
        t = random.random() * 2 + 0.5
        self._pauseTimer = reactor.callLater(t, self.pauseAndReconsider)

        # Decide whether to jump or drop.
        if self.player.isAttachedToWall():
            verticalActions = ['none', 'jump', 'drop']
        elif self.player.isOnPlatform():
            verticalActions = ['none', 'jump', 'drop']
        elif self.player.isOnGround():
            verticalActions = ['none', 'jump']
        else:
            verticalActions = ['none']
        action = random.choice(verticalActions)
        if action == 'jump':
            self.doJump()
        elif action == 'drop':
            self.doDrop()

        # Decide on a direction.
        d = random.choice(['left', 'right', 'stop'])
        if d == 'left':
            self.doAimAt(-pi/2.)
            self.doMoveLeft()
        elif d == 'right':
            self.doAimAt(pi/2.)
            self.doMoveRight()
        else:
            self.doStop()

class AlphaAI(AI):
    nick = 'AlphaAI'

    def start(self):
        self.xdir = 'left'
        self.dead = True

        self.clRespawn = None
        self.clChangeXDir = None
        self.clJump = None
        self.clDrop = None
        self.clShoot = None

        self._launchDeadCallLaters(0)

    def _launchAliveCallLaters(self):
        self._cancelAliveCallLaters()
        self.clChangeXDir = reactor.callLater(0, self.changeXDir)
        self.clJump = reactor.callLater(0, self.jumpAgain)
        self.clDrop = reactor.callLater(0, self.drop)
        self.clShoot = reactor.callLater(0, self.shoot)

    def _cancelAliveCallLaters(self):
        if self.clChangeXDir is not None:
            self.clChangeXDir.cancel()
            self.clChangeXDir = None
        if self.clJump is not None:
            self.clJump.cancel()
            self.clJump = None
        if self.clDrop is not None:
            self.clDrop.cancel()
            self.clDrop = None
        if self.clShoot is not None:
            self.clShoot.cancel()
            self.clShoot = None

    def _launchDeadCallLaters(self, respawnTime=None):
        if respawnTime == None:
            respawnTime = self.player.respawnGauge
        self._cancelDeadCallLaters()
        self.clRespawn = reactor.callLater(respawnTime, self.tryRespawn)

    def _cancelDeadCallLaters(self):
        if self.clRespawn is not None:
            self.clRespawn.cancel()
            self.clRespawn = None

    def died(self, killerId):
        self.dead = True
        self._cancelAliveCallLaters()
        self._launchDeadCallLaters()
        self.aimAtActionZone()

    def respawned(self):
        self.dead = False
        self._cancelDeadCallLaters()
        self._launchAliveCallLaters()

    def aimAtNearestFriendlyZone(self, time = None):
        if time == None:
            time = self.player.respawnGauge
        nearest = None
        for zone in self.world.zones:
            if zone.orbOwner == self.player.team:
                if nearest == None or (distance(zone.defn.pos, self.player.pos)
                        < distance(self.player.pos, nearest.defn.pos)):
                    nearest = zone
        if nearest == None:
            # Stop moving
            self.aimAtPoint(self.player.pos, time)
        else:
            self.aimAtPoint(nearest.defn.pos, time)

    def aimAtActionZone(self, time = None):
        if time == None:
            time = self.player.respawnGauge
        zone = self.getBestRespawnZone()

        self.aimAtPoint(zone.defn.pos, time)

    def getBestRespawnZone(self):
        best, score = None, -1000
        for zone in self.world.zones:
            thisScore = self.getRespawnScore(zone)

            if thisScore > score:
                best, score = zone, thisScore
        return best

    def getRespawnScore(self, zone):
        thisScore = 0
        threat = False
        try:
            team = self.player.team
        except Abort:
            return 0
        if zone.orbOwner == team:
            for adjDef, open in zone.defn.zones_AdjInfo():
                adj = self.world.zoneWithDef[adjDef]
                # Find boundary zone.
                if adj.orbOwner == None:
                    if open:
                        thisScore += 3
                elif adj.orbOwner != team:
                    threat = True
                    if open:
                        thisScore += 5
                if open:
                    # Add 2 points for each unmarked enemy in an open, adjacent
                    # zone
                    thisScore += self.numUnmarkedEnemies(adj) * 2
            if threat == False:
                # No threat, since no enemy adjacent zones
                return thisScore
            else:
                thisScore += 5

            # And 20 points for each unmarked enemy in this zone
            thisScore += self.numUnmarkedEnemies(zone) * 20
        return thisScore

    def numUnmarkedEnemies(self, zone):
        score = 0
        for player in zone.players:
            if player.team == self.player.team:
                score -= 1
            else:
                score += 1
        return max(score, 0)

    def aimAtNearestEnemy(self):
        nearest = None
        thisPlayer = self.player
        for player in self.world.players:
            if (not player.isFriendsWith(thisPlayer) and not player.ghost and
                    not player.turret):
                if nearest == None or (distance(player.pos, thisPlayer.pos) <
                        distance(thisPlayer.pos, nearest.pos)):
                    nearest = player
        if nearest is not None:
            # Add uncertainty
            pos = (nearest.pos[0] + (random.random() * 80 - 40),
                   nearest.pos[1] + (random.random() * 80 - 40))
            self.aimAtPoint(pos)

    def aimAtPoint(self, pos, timeLeft = None):
        dx = pos[0] - self.player.pos[0]
        dy = pos[1] - self.player.pos[1]
        theta = atan2(dx, -dy)
        thrust = 1.0
        if timeLeft is not None:
            dist = (dx ** 2 + dy ** 2) ** 0.5
            maxSpeed = self.world.physics.playerMaxGhostVel
            if timeLeft <= 0:
                speedReq = maxSpeed
            else:
                speedReq = dist / timeLeft

            if speedReq < maxSpeed:
                thrust = speedReq / maxSpeed
        self.doAimAt(theta, thrust)

    def tryRespawn(self):
        if self.dead:
            self.aimAtActionZone()
            self.clRespawn = reactor.callLater(0.5, self.tryRespawn)
            self.doRespawn()

    def changeXDir(self):
        t = random.random() * 5 + 3
        self.clChangeXDir = reactor.callLater(t, self.changeXDir)
        if self.xdir == 'left':
            self.xdir = 'right'
            self.doAimAt(pi/2.)
            self.doMoveRight()
        else:
            self.xdir = 'left'
            self.doAimAt(-pi/2.)
            self.doMoveLeft()

    def drop(self):
        self.clDrop = reactor.callLater(random.random()*3+1.5, self.drop)
        self.doDrop()

    def jumpAgain(self):
        self.clJump = reactor.callLater(random.random()*0.5+0.5, self.stopJump)
        self.doJump()

    def stopJump(self):
        self.clJump = reactor.callLater(random.random()*1.5, self.jumpAgain)
        self.doStopJump()

    def shoot(self):
        self.clShoot = reactor.callLater(random.random()*.5+.4, self.shoot)
        self.aimAtNearestEnemy()
        self.doShoot()

    def zoneTagged(self, zoneId, playerId):
        # In case our zone was tagged
        self.aimAtActionZone()

from weakref import WeakKeyDictionary
class Node(object):
    '''
    Used by PathFindingAI.
    '''
    def __init__(self, obstacle, i, n):
        self.obstacle = obstacle
        self.grabbable = obstacle.grabbable
        self.drop = obstacle.drop

        n = n + 0.
        self.pt1 = (obstacle.pt1[0] + obstacle.deltaPt[0] * i / n,
                obstacle.pt1[1] + obstacle.deltaPt[1] * i / n)
        self.deltaPt = (obstacle.deltaPt[0] / n,
                obstacle.deltaPt[1] / n)

    def getPosition(self):
        return self.obstacle.getPosition()

    def comparePoint(self, point):
        x, y = point
        dX, dY = self.deltaPt
        x1, y1 = self.pt1
        if dX > 0:
            if x < x1:
                return -1
            if x > x1 + dX:
                return 1
        elif dX < 0:
            if x > x1:
                return -1
            if x < x1 + dX:
                return 1
        if dY > 0:
            if y < y1:
                return -1
            if y > y1 + dY:
                return 1
        elif dY < 0:
            if y > y1:
                return -1
            if y < y1 + dY:
                return 1
        return 0

