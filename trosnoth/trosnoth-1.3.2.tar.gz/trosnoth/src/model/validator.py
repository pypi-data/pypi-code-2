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
from trosnoth.src.utils.components import Component, handler, Plug
from trosnoth.src.messages import (ChatMsg, BuyUpgradeMsg, PlayerStarsSpentMsg,
        PlayerHasUpgradeMsg, CannotBuyUpgradeMsg, DeleteUpgradeMsg,
        SetCaptainMsg, TeamIsReadyMsg, RespawnRequestMsg, CannotRespawnMsg,
        RespawnMsg, FireShotMsg, ShootMsg, JoinRequestMsg, CannotJoinMsg,
        JoinApproved, UpdatePlayerStateMsg, AimPlayerAtMsg, RemovePlayerMsg)
from trosnoth.src.model.universe import Abort
from trosnoth.src.model.upgrades import Turret, MinimapDisruption
from trosnoth.src.model.universe_base import GameState

EDGE_TURRET_BOUNDARY = 100
ORB_TURRET_BOUNDARY = 150

class Validator(Component):
    '''
    Checks the validity of messages from the interface's controller plug
    against a universe.
    '''
    agentRequests = Plug()
    gameRequests = Plug()
    gameEvents = Plug()
    agentEvents = Plug()

    def __init__(self, world, maxPlayers=8):
        super(Validator, self).__init__()
        self.world = world
        self.maxPlayers = maxPlayers

    @gameEvents.defaultHandler
    def passOn(self, msg):
        self.agentEvents.send(msg)

    @handler(ShootMsg, agentRequests)
    def reqFireShot(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            shotType = player.getShotType()
            if shotType is None:
                return

            xpos, ypos = player.pos
            self.gameRequests.send(FireShotMsg(msg.playerId, player.angleFacing,
                    xpos, ypos, shotType))
        except Abort:
            pass

    @handler(BuyUpgradeMsg, agentRequests)
    def reqUpgrade(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player.upgrade is not None:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'A',
                        msg.tag))
                return
            elif self.world.gameState in (GameState.PreGame, GameState.Starting):
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'P',
                        msg.tag))
                return
            elif player.ghost:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'D',
                        msg.tag))
                return

            upgrade = self.world.getUpgradeType(msg.upgradeType)
            if self.world.getTeamStars(player.team) < upgrade.requiredStars:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, 'N',
                        msg.tag))
                return

            reason = self._checkUpgradeConditions(player, upgrade)
            if reason is not None:
                self.agentEvents.send(CannotBuyUpgradeMsg(msg.playerId, reason,
                        msg.tag))
                return

            self._processUpgradePurchase(player, upgrade)
        except Abort:
            pass

    def _checkUpgradeConditions(self, player, upgrade):
        '''
        Checks whether the conditions are satisfied for the given player to be
        able to purchase an upgrade of the given kind. Returns None if no
        condition is violated, otherwise returns a one-byte reason code for why
        the upgrade cannot be purchased.
        '''
        if upgrade is Turret:
            zone = player.currentZone
            if zone.zoneOwner != player.team:
                return 'F'
            if zone.turretedPlayer is not None:
                return 'T'
            if player.currentMapBlock.fromEdge(player) < EDGE_TURRET_BOUNDARY:
                return 'E'

            distanceFromOrb = ((zone.defn.pos[0] - player.pos[0]) ** 2 +
                    (zone.defn.pos[1] - player.pos[1]) ** 2) ** 0.5
            if distanceFromOrb < ORB_TURRET_BOUNDARY:
                return 'O'
        elif upgrade is MinimapDisruption:
            if player.team.opposingTeam.minimapDisrupted:
                return 'M'

        return None

    def _processUpgradePurchase(self, player, upgrade):
        '''
        Sends the required sequence of messages to gameRequests to indicate that the
        upgrade has been purchased by the player.
        '''
        remaining = upgrade.requiredStars

        # Take from the purchasing player first.
        fromPurchaser = min(player.stars, remaining)
        self.gameRequests.send(PlayerStarsSpentMsg(player.id, fromPurchaser))
        remaining -= fromPurchaser

        # Now take evenly from other team members.
        if remaining > 0:
            players = []
            totalStars = 0
            for p in self.world.players:
                if p.team == player.team and p.id != player.id and p.stars > 0:
                    players.append(p)
                    totalStars += p.stars
            # Order by descending number of stars
            # Shuffle first to avoid biasing any player with the same number of stars as another
            random.shuffle(players)
            players.sort(cmp=lambda p1,p2:cmp(p1.stars, p2.stars))
            players.reverse()
            
            for p in players:
                fraction = remaining / (totalStars + 0.)
                toGive = int(round(fraction * p.stars))
                remaining -= toGive
                totalStars -= p.stars
                self.gameRequests.send(PlayerStarsSpentMsg(p.id, toGive))
            # Everything should add up
            assert(remaining == 0)
            assert(totalStars == 0)

        self.gameRequests.send(PlayerHasUpgradeMsg(player.id, upgrade.upgradeType))

    @handler(JoinRequestMsg, agentRequests)
    def reqJoinGame(self, msg):
        teamId = msg.teamId
        nick = msg.nick.decode()
        teamPlayerCounts = self._getTeamPlayerCounts()
        if teamId == '\x00':
            teamId = self._autoSelectTeam(teamPlayerCounts)

        if teamPlayerCounts.get(teamId, 0) >= self.maxPlayers:
            self.agentEvents.send(CannotJoinMsg('F', msg.teamId, msg.tag))
            return
        if self.world.gameState == GameState.Ended:
            self.agentEvents.send(CannotJoinMsg('O', msg.teamId, msg.tag))
            return

        for player in self.world.players:
            if player.nick.lower() == nick.lower():
                self.agentEvents.send(CannotJoinMsg('N', msg.teamId, msg.tag))
                return

        self.gameRequests.send(JoinApproved(teamId, msg.tag, self._selectZone(
                teamId), msg.nick))

    def _selectZone(self, teamId):
        # TODO: pick a zone close to the action
        zones = [z for z in self.world.map.zones if z.orbOwner is not None and
                z.orbOwner.id == teamId]
        return random.choice(zones).id

    def _getTeamPlayerCounts(self):
        '''
        Returns a mapping from team id to number of players currently on that
        team.
        '''
        playerCounts = {}
        for player in self.world.players:
            playerCounts[player.team.id] = playerCounts.get(player.team.id, 0
                    ) + 1
        return playerCounts

    def _autoSelectTeam(self, playerCounts):
        '''
        Returns the team id of one of the teams with the smallest number of
        players.
        '''
        minCount = len(self.world.players) + 1
        minTeams = []
        for team in self.world.teams:
            count = playerCounts.get(team.id, 0)
            if count < minCount:
                minCount = count
                minTeams = [team.id]
            elif count == minCount:
                minTeams.append(team.id)
        return random.choice(minTeams)

    @handler(RespawnRequestMsg, agentRequests)
    def reqRespawn(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if self.world.gameState in (GameState.PreGame, GameState.Starting):
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'P', msg.tag))
            elif not player.ghost:
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'A', msg.tag))
            elif player.respawnGauge > 0:
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'T', msg.tag))
            elif player.currentZone.orbOwner != player.team:
                self.agentEvents.send(CannotRespawnMsg(msg.playerId, 'E', msg.tag))
            else:
                self.gameRequests.send(RespawnMsg(msg.playerId,
                        player.currentZone.id))
        except Abort:
            pass

    @handler(UpdatePlayerStateMsg, agentRequests)
    def reqUpdateState(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player._state[msg.stateKey] == msg.value:
                if not msg.value:
                    return
                self.gameRequests.send(UpdatePlayerStateMsg(msg.playerId, False,
                        msg.stateKey))
            self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(AimPlayerAtMsg, agentRequests)
    def reqAimPlayer(self, msg):
        thrust = min(1, max(0, msg.thrust))
        angle = (msg.angle + pi) % (2 * pi) - pi
        self.gameRequests.send(AimPlayerAtMsg(msg.playerId, angle, thrust))

    @handler(DeleteUpgradeMsg, agentRequests)
    def reqDelUpgrade(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if (player.upgrade is not None and
                    player.upgrade.upgradeType != 'g'):
                self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(RemovePlayerMsg, agentRequests)
    def reqRemovePlayer(self, msg):
        try:
            self.world.getPlayer(msg.playerId)
            self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(SetCaptainMsg, agentRequests)
    def reqSetCaptain(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player.team.captain is None:
                self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(TeamIsReadyMsg, agentRequests)
    def reqTeamReady(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if player.team.captain == player:
                self.gameRequests.send(msg)
        except Abort:
            pass

    @handler(ChatMsg, agentRequests)
    def chatSent(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            if msg.kind == 't' and msg.targetId != player.team.id:
                # Cannot sent to opposing team.
                return
            if msg.kind == 'p':
                self.world.getPlayer(msg.targetId)  # Check player exists.
            self.gameRequests.send(msg)
        except Abort:
            pass
