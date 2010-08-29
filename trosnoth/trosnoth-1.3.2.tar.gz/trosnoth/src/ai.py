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

from math import pi
import random
from trosnoth.src.utils.components import Component, Plug, handler
from trosnoth.src.messages import (ChatMsg, TaggingZoneMsg, PlayerStarsSpentMsg,
        PlayerHasUpgradeMsg, DeleteUpgradeMsg, CannotBuyUpgradeMsg,
        GameStartMsg, GameOverMsg, StartingSoonMsg, SetCaptainMsg,
        TeamIsReadyMsg, SetTeamNameMsg, SetGameModeMsg, ShotFiredMsg, ShootMsg,
        KillShotMsg, RespawnMsg, CannotRespawnMsg, RespawnRequestMsg,
        PlayerKilledMsg, PlayerUpdateMsg, PlayerHitMsg, JoinRequestMsg,
        JoinSuccessfulMsg, CannotJoinMsg, AddPlayerMsg, UpdatePlayerStateMsg,
        AimPlayerAtMsg, ConnectionLostMsg, RemovePlayerMsg)
from trosnoth.src.model.universe import Abort
from trosnoth.src.utils.math import distance
from math import atan2

from twisted.internet import reactor

class AI(Component):
    '''
    Base class for an AI agent.
    '''
    eventPlug = Plug()
    requestPlug = Plug()

    def __init__(self, world):
        Component.__init__(self)
        self.world = world
        self._playerIds = []
        self._reqNicks = {}

    @handler(RemovePlayerMsg, eventPlug)
    @handler(DeleteUpgradeMsg, eventPlug)
    @handler(GameStartMsg, eventPlug)
    @handler(PlayerStarsSpentMsg, eventPlug)
    @handler(PlayerHasUpgradeMsg, eventPlug)
    @handler(KillShotMsg, eventPlug)
    @handler(ShotFiredMsg, eventPlug)
    @handler(CannotBuyUpgradeMsg, eventPlug)
    @handler(UpdatePlayerStateMsg, eventPlug)
    @handler(AimPlayerAtMsg, eventPlug)
    @handler(GameOverMsg, eventPlug)
    @handler(StartingSoonMsg, eventPlug)
    @handler(SetCaptainMsg, eventPlug)
    @handler(TeamIsReadyMsg, eventPlug)
    @handler(SetTeamNameMsg, eventPlug)
    @handler(SetGameModeMsg, eventPlug)
    @handler(PlayerUpdateMsg, eventPlug)
    @handler(ConnectionLostMsg, eventPlug)
    @handler(PlayerHitMsg, eventPlug)
    @handler(ChatMsg, eventPlug)
    def _ignoreMessage(self, msg):
        # TODO: Make methods which handle these.
        pass

    def doJoinGame(self, nick, team=None):
        if team is None:
            teamId = '\x00'
        else:
            teamId = team.id
        reqTag = random.randrange(1<<32)
        return self._joinGame(nick, teamId, reqTag, 1)

    def _joinGame(self, nick, teamId, reqTag, attempt):
        self._reqNicks[reqTag] = (nick, attempt)

        if attempt > 1:
            nick = '%s-%d' % (nick, attempt)
        self.requestPlug.send(JoinRequestMsg(teamId, reqTag, nick.encode()))

        return reqTag

    @handler(JoinSuccessfulMsg, eventPlug)
    def _joinSuccessful(self, msg):
        if msg.tag in self._reqNicks:
            del self._reqNicks[msg.tag]
        self._playerIds.append(msg.playerId)
        self.joinSuccessful(msg.playerId, msg.tag)
    def joinSuccessful(self, playerId, reqTag):
        raise NotImplementedError

    @handler(CannotJoinMsg, eventPlug)
    def _joinFailed(self, msg):
        r = msg.reasonId
        if msg.tag in self._reqNicks:
            nick, attempt = self._reqNicks.pop(msg.tag)
        else:
            nick = None

        if r == 'F':
            self.joinFailed('full')
        elif r == 'O':
            self.joinFailed('over')
        elif r == 'W':
            self.joinFailed('wait')
        elif r == 'N':
            if nick is None:
                self.joinFailed('nick')
            else:
                attempt += 1
                self._joinGame(nick, msg.teamId, msg.tag, attempt)
        else:
            self.joinFailed(r)

    def joinFailed(self, reason):
        raise NotImplementedError

    def doMoveRight(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, True,
                stateKey='right'))
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, False,
                stateKey='left'))

    def doMoveLeft(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, True,
                stateKey='left'))
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, False,
                stateKey='right'))

    def doStop(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, False,
                stateKey='right'))
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, False,
                stateKey='left'))

    def doDrop(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, True,
                stateKey='down'))
        reactor.callLater(0.1, self._releaseDropKey, playerId)
    def _releaseDropKey(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, False,
                stateKey='down'))

    def doJump(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, True,
                stateKey='jump'))

    def doStopJump(self, playerId):
        self.requestPlug.send(UpdatePlayerStateMsg(playerId, False,
                stateKey='jump'))

    def doAimAt(self, playerId, angle, thrust=1.0):
        self.requestPlug.send(AimPlayerAtMsg(playerId, angle, thrust))

    def doShoot(self, playerId):
        self.requestPlug.send(ShootMsg(playerId))

    def doRespawn(self, playerId):
        '''
        Attempts to respawn.
        '''
        self.requestPlug.send(RespawnRequestMsg(playerId,
                random.randrange(1<<32)))

    @handler(RespawnMsg, eventPlug)
    def _respawned(self, msg):
        if msg.playerId in self._playerIds:
            self.respawned(msg.playerId)

    @handler(CannotRespawnMsg, eventPlug)
    def _respawnFailed(self, msg):
        self.respawnFailed(msg.playerId)

    def respawned(self, playerId):
        raise NotImplementedError
    def respawnFailed(self, playerId):
        raise NotImplementedError

    @handler(PlayerKilledMsg, eventPlug)
    def _playerKilled(self, msg):
        if msg.targetId in self._playerIds:
            self.died(msg.targetId, msg.killerId)

    def died(self, playerId, killerId):
        raise NotImplementedError

    def doBecomeCaptain(self, playerId):
        self.requestPlug.send(SetCaptainMsg(playerId))

    def doTeamReady(self, playerId):
        if playerId is None:
            playerId = random.choice(self._playerIds)
        self.requestPlug.send(TeamIsReadyMsg(playerId))

    def start(self):
        raise NotImplementedError

    @handler(TaggingZoneMsg, eventPlug)
    def _zoneTagged(self, msg):
        self.zoneTagged(msg.zoneId, msg.playerId)

    def zoneTagged(self, zoneId, playerId):
        pass

    @handler(AddPlayerMsg, eventPlug)
    def _playerAdded(self, msg):
        self.playerAdded(msg.playerId)

    def playerAdded(self, id):
        pass

class SingleAI(AI):
    def doMoveRight(self):
        AI.doMoveRight(self, self.playerId)

    def doMoveLeft(self):
        AI.doMoveLeft(self, self.playerId)

    def doStop(self):
        AI.doStop(self, self.playerId)

    def doDrop(self):
        AI.doDrop(self, self.playerId)

    def doJump(self):
        AI.doJump(self, self.playerId)

    def doStopJump(self):
        AI.doStopJump(self, self.playerId)

    def doAimAt(self, angle, thrust=1.0):
        AI.doAimAt(self, self.playerId, angle, thrust)

    def doShoot(self):
        AI.doShoot(self, self.playerId)

    def doRespawn(self):
        AI.doRespawn(self, self.playerId)

    def doBecomeCaptain(self):
        AI.doBecomeCaptain(self, self.playerId)

    def doTeamReady(self):
        AI.doTeamReady(self, self.playerId)

        
class AlphaAI(SingleAI):
    def __init__(self, world):
        AI.__init__(self, world)
        self.xdir = 'left'
        self.dead = True
        self.playerId = None

        self.clRespawn = None
        self.clChangeXDir = None
        self.clJump = None
        self.clDrop = None
        self.clShoot = None

    def start(self):
        self.doJoinGame('AI-Alpha')

    def joinSuccessful(self, playerId, tag):
        self.playerId = playerId
        reactor.callLater(2, self.doBecomeCaptain)
        reactor.callLater(3, self.doTeamReady)
        self._launchDeadCallLaters(10.5)
        self.aimAtActionZone(10.5)

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

    def _launchDeadCallLaters(self, respawnTime = None):
        if respawnTime == None:
            respawnTime = self.world.getPlayer(self.playerId).respawnGauge
        self._cancelDeadCallLaters()
        self.clRespawn = reactor.callLater(respawnTime, self.tryRespawn)

    def _cancelDeadCallLaters(self):
        if self.clRespawn is not None:
            self.clRespawn.cancel()
            self.clRespawn = None

    def joinFailed(self, reason):
        pass

    def died(self, playerId, killerId):
        self.dead = True
        self._cancelAliveCallLaters()
        self._launchDeadCallLaters()
        self.aimAtActionZone()

    def respawned(self, playerId):
        self.dead = False
        self._cancelDeadCallLaters()
        self._launchAliveCallLaters()

    def aimAtNearestFriendlyZone(self, time = None):
        if time == None:
            time = self.world.getPlayer(self.playerId).respawnGauge
        nearest = None
        for zone in self.world.zones:
            if zone.orbOwner == self.world.getPlayer(self.playerId).team:
                if nearest == None or (distance(zone.defn.pos, self.world.getPlayer(self.playerId).pos) < distance(self.world.getPlayer(self.playerId).pos, nearest.defn.pos)):
                    nearest = zone
        if nearest == None:
            # Stop moving
            self.aimAtPoint(self.world.getPlayer(self.playerId).pos, time)
        else:
            self.aimAtPoint(nearest.defn.pos, time)

    def aimAtActionZone(self, time = None):
        if time == None:
            time = self.world.getPlayer(self.playerId).respawnGauge
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
            team = self.world.getPlayer(self.playerId).team
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
                    # Add 2 points for each unmarked enemy in an open, adjacent zone
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
            if player.team == self.world.getPlayer(self.playerId).team:
                score -= 1
            else:
                score += 1
        return max(score, 0)

    def aimAtNearestEnemy(self):
        nearest = None
        for player in self.world.players:
            if player.team != self.world.getPlayer(self.playerId).team and not player.ghost and not player.turret:
                if nearest == None or (distance(player.pos, self.world.getPlayer(self.playerId).pos) < distance(self.world.getPlayer(self.playerId).pos, nearest.pos)):
                    nearest = player
        if nearest is not None:
            # Add uncertainty
            pos = (nearest.pos[0] + (random.random() * 80 - 40),
                   nearest.pos[1] + (random.random() * 80 - 40))
            self.aimAtPoint(pos)

    def aimAtPoint(self, pos, timeLeft = None):
        try:
            player = self.world.getPlayer(self.playerId)
        except Abort:
            return
        dx = pos[0] - player.pos[0]
        dy = pos[1] - player.pos[1]
        theta = atan2(dx, -dy)
        thrust = 1.0
        if timeLeft is not None:
            dist = (dx ** 2 + dy ** 2) ** 0.5
            maxSpeed = player.maxGhostVel
            if timeLeft <= 0:
                speedReq = maxSpeed
            else:
                speedReq = dist / timeLeft
            
            if speedReq < maxSpeed:
                thrust = speedReq / maxSpeed
        self.doAimAt(theta, thrust)

    def respawnFailed(self, playerId):
        pass
        
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
