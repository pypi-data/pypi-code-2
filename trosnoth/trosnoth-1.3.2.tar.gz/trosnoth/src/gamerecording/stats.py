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

from trosnoth.src.utils.components import Component, Plug, handler
from trosnoth.src.messages import (TaggingZoneMsg, PlayerStarsSpentMsg,
        GameStartMsg, GameOverMsg, ShotFiredMsg, RespawnMsg, PlayerKilledMsg,
        PlayerHitMsg, AddPlayerMsg, RemovePlayerMsg, PlayerHasUpgradeMsg)

from trosnoth.src.utils.utils import timeNow, new
from collections import defaultdict
from trosnoth.src.utils.jsonImport import json
from trosnoth.src.model.upgrades import upgradeOfType, upgradeNames

class KillMode(object):
    NORMAL, HUNTER, RABBIT, NONE = new(4)

# Known Issues:
#  * If a player shoots a turret, a shield, or a phase shift,
#    their shot will not register as hit.
#
# Things to check:
# * Does it count the very last tag, or has the game terminated before that?

class PlayerStatKeeper(object):
    '''Maintains the statistics for a particular player object'''
    def __init__(self, player):
        self.player = player
        
        # A: Recorded [A]ll game (including post-round)
        # G: Recorded during the main [G]ame only
        # P: Recorded [P]ost-Game only
        self.kills = 0           # G Number of kills they've made
        self.deaths = 0          # G Number of times they've died
        self.zoneTags = 0        # G Number of zones they've tagged
        self.zoneAssists = 0     # G Number of zones they've been in when their team tags it
        self.shotsFired = 0      # A Number of shots they've fired
        self.shotsHit = 0        # A Number of shots that have hit a target
        self.starsEarned = 0     # G Aggregate total of stars earned
        self.starsUsed = 0       # G Aggregate total of stars used
##        self.starsWasted = 0     # G Aggregate total of stars died with
        self.roundsWon = 0       # . Number of rounds won
        self.roundsLost = 0      # . Number of rounds lost

        self.killsAsRabbit = 0   # P Number of kills they've made as a rabbit
        self.rabbitsKilled = 0   # P Number of rabbits they've killed

        self.playerKills = defaultdict(int)    # A Number of kills against individual people
        self.playerDeaths = defaultdict(int)   # A Number of deaths from individual people
        self.upgradesUsed = defaultdict(int)   # G Number of each upgrade used
                
        self.timeAlive = 0.0     # G Total time alive
        self.timeDead = 0.0      # G Total time dead
        self.timeRabbit = 0.0    # P Total time alive as a rabbit

        self.killStreak = 0      # G Number of kills made without dying
        self.currentKillStreak = 0
        self.tagStreak = 0       # G Number of zones tagged without dying
        self.currentTagStreak = 0
        self.aliveStreak = 0.0   # G Greatest time alive in one life
        self.lastTimeRespawned = None
        self.rabbitStreak = 0.0  # P Greatest time alive as a rabbit
        self.lastRabbitTime = None
        self.lastTimeDied = None
        self.lastTimeSaved = None

        self.killMode = KillMode.NORMAL        

    def shotFired(self):
        self.shotsFired += 1

    def died(self, killer):
        if self.killMode == KillMode.NORMAL:
            self.deaths += 1
            self.playerDeaths[killer] += 1
        self._allStreaksOver()
        self.lastTimeDied = timeNow()

    def goneFromGame(self):
        self._allStreaksOver()

    def gameOver(self, winningTeamId):
        self.saveAllStreaks()
        if winningTeamId == '\x00':
            # Draw. Do nothing
            self.killMode = KillMode.NONE
        elif winningTeamId == self.player.team.id:
            self.roundsWon += 1
            self.killMode = KillMode.HUNTER
        else:
            self.roundsLost += 1
            self.killMode = KillMode.RABBIT
            if not self.player.ghost:
                # This player is a rabbit
                self.lastRabbitTime = timeNow()

    def _allStreaksOver(self):
        self.saveAllStreaks()
        self.lastTimeSaved = None
        
        self.currentKillStreak = 0
        self.currentTagStreak = 0
        self.lastTimeRespawned = None
        self.lastRabbitTime = None

    def killed(self, victim):
        if self.killMode == KillMode.NORMAL:
            self.kills += 1
            self.playerKills[victim] += 1
            self.currentKillStreak += 1
            self.starsEarned += 1
        elif self.killMode == KillMode.HUNTER:
            self.rabbitsKilled += 1
        elif self.killMode == KillMode.RABBIT:
            self.killsAsRabbit += 1

    def respawned(self):
        self.lastTimeRespawned = timeNow()
        self.saveAllStreaks()
        self.lastTimeDied = None
        self.lastTimeSaved = None

    def zoneTagged(self):
        if self.killMode == KillMode.NORMAL:
            self.zoneTags += 1
            self.currentTagStreak += 1
            self.starsEarned += 1

    def tagAssist(self):
        if self.killMode == KillMode.NORMAL:
            self.zoneAssists += 1

    def shotHit(self):
        self.shotsHit += 1

    def usedStars(self, stars):
        if self.killMode == KillMode.NORMAL:
            self.starsUsed += stars

    def upgradeUsed(self, upgradeType):
        if self.killMode == KillMode.NORMAL:
            self.upgradesUsed[upgradeType] += 1
        self.saveAllStreaks()

    def totalPoints(self):
        points = 0
        points += self.kills        * 10
        points += self.deaths       * 1
        points += self.zoneTags     * 20
        points += self.zoneAssists  * 5
        points += self._accuracyPoints()

        return points

    def _accuracyPoints(self):
        if self.shotsFired == 0:
            return 0
        return ((self.shotsHit ** 2) / self.shotsFired) * 30

    def accuracy(self):
        if self.shotsFired == 0:
            return 0
        return self.shotsHit / self.shotsFired

    def saveAllStreaks(self):
        now = timeNow()
        if self.player.ghost:
            if self.lastTimeDied is not None:
                self.timeDead += (now - self.lastTimeDied)
        else:
            self.killStreak = max(self.killStreak, self.currentKillStreak)
            self.tagStreak = max(self.tagStreak, self.currentTagStreak)
            
            if self.lastTimeRespawned is not None:
                currentAliveStreak = now - self.lastTimeRespawned
                if self.lastTimeSaved != None:
                    currentTimeAliveToAdd = now - self.lastTimeSaved
                else:
                    currentTimeAliveToAdd = currentAliveStreak                    
                self.aliveStreak = max(self.aliveStreak, currentAliveStreak)
                self.timeAlive += currentTimeAliveToAdd
                                                                
            if self.lastRabbitTime is not None:
                currentRabbitStreak = now - self.lastRabbitTime
                self.rabbitStreak = max(self.rabbitStreak, currentRabbitStreak)
                if self.lastTimeSaved != None:
                    currentTimeAliveToAdd = now - self.lastTimeSaved
                else:
                    currentTimeAliveToAdd = currentRabbitStreak
                self.timeRabbit += currentTimeAliveToAdd
        self.lastTimeSaved = now

    # Probably fallible, as players could rejoin with the same name.
    def statDict(self):
        stats = {}
        for val in 'aliveStreak', 'deaths', 'killStreak', 'kills', 'killsAsRabbit', \
            'rabbitStreak', 'rabbitsKilled', 'roundsLost', 'roundsWon', 'shotsFired', \
            'shotsHit', 'starsEarned', 'starsUsed', \
            'tagStreak', 'timeAlive', 'timeDead',\
            'timeRabbit', 'upgradesUsed', 'zoneAssists', 'zoneTags':
            stats[val] = getattr(self, val)
        # We've stored these dicts as player objects (meaning rejoins may be credited in two places)
        # Here, we combine them by aggregating on player nick (which should be the same)
        for attribute in 'playerKills', 'playerDeaths':
            dictionary = getattr(self, attribute)
            newDict = {}
            for item in dictionary.iteritems():
                newDict[item[0].nick] = item[1]
            stats[attribute] = newDict
                
            
        return stats

    def rejoined(self, player):
        self.player = player
        
        

class StatKeeper(Component):
    inPlug = Plug()

    def __init__(self, world, filename):
        Component.__init__(self)
        self.world = world
        self.filename = filename
        # In case the server dies prematurely, it's nice
        # To at least have the file there so that
        # future games don't accidentally point to this one.
        file = open(self.filename, 'w')
        file.write('{}')
        file.close()
        # A mapping of player ids to statLists
        # (Contains only players currently in the game)
        self.playerStatList = {}
        # A list of all statLists
        # (regardless of in-game status)
        self.allPlayerStatLists = []

    def save(self):
        stats = {}
        for playerStat in self.allPlayerStatLists:
            stats[playerStat.player.nick] = playerStat.statDict()
        # TODO: remove cyclic dependency by putting checkJson in a common location
        from trosnoth.src.gamerecording.gamerecorder import checkJson
        checkJson()
        file = open(self.filename, 'w')
        statString = json.dumps(stats, indent = 3)
        file.write(statString)
        file.flush()
        file.close()

    @inPlug.defaultHandler
    def ingnore(self, msg):
        pass

    @handler(GameStartMsg, inPlug)
    def gameStarted(self, msg):
        pass
    
    @handler(RespawnMsg, inPlug)
    def playerRespawned(self, msg):
        self.playerStatList[msg.playerId].respawned()
    
    @handler(TaggingZoneMsg, inPlug)
    def zoneTagged(self, msg):
        self.playerStatList[msg.playerId].zoneTagged()
        zone = self.world.getZone(msg.zoneId)
        player = self.world.getPlayer(msg.playerId)
        for assistant in zone.players:
            if assistant.team == player.team and assistant != player:
                self.playerStatList[assistant.id].tagAssist()

    @handler(PlayerKilledMsg, inPlug)
    def playerKilled(self, msg):
        if msg.killerId == '\x00':
            # TODO: How should we score this?
            return
        self.playerStatList[msg.targetId].died(self.world.getPlayer(msg.killerId))
        self.playerStatList[msg.killerId].killed(self.world.getPlayer(msg.targetId))
        if msg.shotId != 0:
            self.playerStatList[msg.killerId].shotHit()
        
        
    @handler(PlayerStarsSpentMsg, inPlug)
    def usedStars(self, msg):
        self.playerStatList[msg.playerId].usedStars(msg.count)
    
    @handler(AddPlayerMsg, inPlug)
    def addPlayer(self, msg):
        player = self.world.getPlayer(msg.playerId)
        statkeeper = None
        for sl in self.allPlayerStatLists:
            if sl.player.nick == player.nick:
                statkeeper = sl
                statkeeper.rejoined(player)
        if statkeeper is None:
            statkeeper = PlayerStatKeeper(player)
            self.allPlayerStatLists.append(statkeeper)
        self.playerStatList[msg.playerId] = statkeeper
        self.save()

    @handler(RemovePlayerMsg, inPlug)
    def removePlayer(self, msg):
        self.playerStatList[msg.playerId].goneFromGame()
        # Just remove this from the list of current players
        # (retain in list of all stats)
        del self.playerStatList[msg.playerId]

    @handler(GameOverMsg, inPlug)
    def gameOver(self, msg):
        # Only credit current players for game over
        for playerStat in self.playerStatList.values():
            playerStat.gameOver(msg.teamId)
        self.save()

    @handler(ShotFiredMsg, inPlug)
    def shotFired(self, msg):
        self.playerStatList[msg.playerId].shotFired()

    @handler(PlayerHitMsg, inPlug)
    def playerHit(self, msg):
        self.playerStatList[msg.shooterId].shotHit()

    @handler(PlayerHasUpgradeMsg, inPlug)
    def upgradeUsed(self, msg):
        upgradeType = upgradeOfType[msg.upgradeType]
        upgradeString = upgradeNames[upgradeType]
        self.playerStatList[msg.playerId].upgradeUsed(upgradeString)

    def stop(self):
        self.save()