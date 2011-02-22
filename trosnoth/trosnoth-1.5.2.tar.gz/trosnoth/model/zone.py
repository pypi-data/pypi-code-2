# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
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

import random
import logging

log = logging.getLogger('zone')

class ZoneDef(object):
    '''Stores static information about the zone.

    Attributes:
        adjacentZones - mapping from adjacent ZoneDef objects to collection of
            map blocks joining the zones.
        id - the zone id
        initialOwner - the team that initially owned this zone,
            represented as a number (0 for neutral, 1 or 2 for a team).
        pos - the coordinates of this zone in the map
    '''
    def __init__(self, id, initialOwnerIndex, xCoord, yCoord):
        self.adjacentZones = {}
        self.id = id
        self.initialOwnerIndex = initialOwnerIndex
        self.pos = xCoord, yCoord
        self.bodyBlocks = []
        self.interfaceBlocks = []

    ##
    # Return a tuple of adjacent zones, and whether each connection is open
    def zones_AdjInfo(self):
        ret = []
        for adj, blocks in self.adjacentZones.iteritems():
            ret.append((adj, not blocks[0].blocked))
        return tuple(ret)

    def __str__(self):
        if self.id == None:
            return 'Z---'
        return 'Z%3d' % self.id

    def randomPosition(self):
        '''
        Returns a random position in this zone.
        '''
        if random.random() * 3 > 1:
            return random.choice(self.bodyBlocks).randomPosition()
        return random.choice(self.interfaceBlocks).randomPositionInZone(self)

class ZoneState(object):
    '''Represents information about a given zone and its state.

    Attributes:
        universe
        zoneOwner - a team
        orbOwner - a team
        players - a Group
        nonPlayers - a Group for ghosts
        taggedThisTime - boolean flag used to compare whether multiple players
            have tagged the zone in one tick
        turretedPlayer - None or a Player

    Attributes which should (eventually) be completely migrated to the zoneDef:
        id
    '''

    def __init__(self, universe, zoneDef):
        self.defn = zoneDef
        self.id = zoneDef.id

        universe.zoneWithDef[zoneDef] = self

        self.universe = universe
        teamIndex = zoneDef.initialOwnerIndex
        if teamIndex is None:
            self.zoneOwner = None
        else:
            self.zoneOwner = universe.teams[teamIndex]

            # Tell the team object that it owns one more zone
            self.zoneOwner.orbGained()
        self.orbOwner = self.zoneOwner
        self.previousOwner = self.orbOwner

        self.players = set()

        # zone.nonPlayers are those players that do not count in zone
        # calculations, such as ghosts and decoys
        self.nonPlayers = set()
        self.taggedThisTime = False
        self.turretedPlayer = None
        self.frozen = False

        self.markedBy = {}

    def __str__(self):
        # Debug: uniquely identify this zone within the universe.
        if self.id == None:
            return 'Z---'
        return 'Z%3d' % self.id

    def tag(self, player):
        '''This method should be called when the orb in this zone is tagged'''
        self.previousOwner = self.orbOwner

        # Inform the team objects
        if self.orbOwner:
            self.orbOwner.orbLost()
        if player is not None:
            team = player.team
            if team is not None:
                team.orbGained()
        else:
            team = None


        if team == None:
            self.orbOwner = None
            self.zoneOwner = None
        else:
            self.orbOwner = team
            allGood = True
            for zoneDef in self.defn.adjacentZones:
                zone = self.universe.zoneWithDef[zoneDef]
                if zone.orbOwner == team:
                    # Allow the adjacent zone to check if it is entirely
                    # surrounded by non-enemy zones
                    zone.checkAgain()
                elif zone.orbOwner == None:
                    pass
                else:
                    allGood = False
            if allGood:
                self.zoneOwner = team
            else:
                self.zoneOwner = None
            player.incrementStars()

    def setOwnership(self, team, dark, marks):
        if self.orbOwner is not None:
            self.orbOwner.orbLost()
        self.orbOwner = team
        if team is not None:
            team.orbGained()
        if dark:
            self.zoneOwner = team
        else:
            self.zoneOwner = None

        markedBy = {}
        for mark in marks:
            markedBy[self.universe.teamWithId[mark]] = True
        self.markedBy = markedBy

    def checkAgain(self):
        '''This method should be called by an adjacent friendly zone that has
        been tagged and gained. It will check to see if it now has all
        surrounding orbs owned by the same team, in which case it will
        change its zone ownership.'''

        # If the zone is already owned, ignore it
        if self.zoneOwner != self.orbOwner and self.orbOwner is not None:
            for zoneDef in self.defn.adjacentZones:
                zone = self.universe.zoneWithDef[zoneDef]
                if zone.orbOwner == self.orbOwner or zone.orbOwner is None:
                    pass
                else:
                    # Found an enemy orb.
                    break
            else:
                # Change zone ownership to orb ownership.
                self.zoneOwner = self.orbOwner

    def checkForOpposingTag(self, team):
        '''In the event that a zone is tagged by a team, this procedure is
        called to see if an opposing team also tags the orb.'''

        xCoord1, yCoord1 = self.defn.pos
        tagDistance = 30
        for player in self.players:
            if player.team != team:
                xCoord2, yCoord2 = player.pos
                distance = ((xCoord1 - xCoord2) ** 2 + (yCoord1 - yCoord2) **
                        2) ** 0.5
                if distance < tagDistance:
                    return True
        return False

    def removePlayer(self, player):
        '''Removes a player from this zone'''
        try:
            if player.ghost:
                self.nonPlayers.discard(player)
            else:
                self.players.discard(player)
        except KeyError, e:
            log.exception(str(e))

    def addPlayer(self, player):
        '''Adds a player to this zone'''
        try:
            if player.ghost:
                if player not in self.nonPlayers:
                    self.nonPlayers.add(player)
            else:
                if player not in self.players:
                    self.players.add(player)
        except KeyError, e:
            log.exception(str(e))

    def getPlayerCounts(self):
        '''
        Returns a mapping from team to the number of players that team has in
        the zone. Does not count rogue players.
        This takes into account the fact that turrets do not count towards
        numerical advantage.
        '''
        result = dict((team, 0) for team in self.universe.teams)

        for player in self.players:
            if player.turret:
                # Turreted players do not count as a player for the purpose
                # of reckoning whether an enemy can capture the orb
                continue
            if player.team is not None:
                result[player.team] += 1
        return result

    def isCapturableBy(self, team):
        '''
        Returns True or False depending on whether this zone can be captured by
        the given team. This takes into account both the zone location and the
        number of players in the zone.
        '''
        return team != self.orbOwner and team in self.getAttackingTeams()

    def isDisputed(self):
        '''
        Returns a value indicating whether this is a disputed zone. A disputed
        zone is defined as a zone which cannot be tagged by any enemy team, but
        could be if there was one more enemy player in the zone.
        '''
        maxPlayers = 0
        state = 'empty'
        for team, count in self.getPlayerCounts().iteritems():
            if count == 0:
                continue
            if maxPlayers > 3:
                if (count > 3 and team != self.orbOwner and
                        self.adjacentToTeam(team)):
                    state = 'capturable'
            elif count > maxPlayers:
                if team != self.orbOwner and self.adjacentToTeam(team):
                    state = 'capturable'
                else:
                    state = 'safe'
                maxPlayers = count
            elif count == maxPlayers:
                state  = 'disputed'
        if state == 'empty':
            for team in self.universe.teams:
                if team != self.orbOwner and self.adjacentToTeam(team):
                    state = 'disputed'
                    break
        return state == 'disputed'

    def getAttackingTeams(self):
        '''
        Checks whether there are any teams which are able to capture this zone.
        If so, returns a set of all such teams, otherwise returns an empty set.
        Does not take into account the fact that a team owns the zone. That is,
        the orb owner may be in this set.
        '''
        return set([t for t in self.getWinningTeams() if
                self.adjacentToTeam(t)])

    def adjacentToTeam(self, team):
        '''
        Returns whether or not this zone is adjacent to a zone whose orb is
        owned by the given team.
        '''
        for adjZoneDef in self.defn.adjacentZones:
            adjZone = self.universe.zoneWithDef[adjZoneDef]
            if adjZone.orbOwner == team:
                return True
        return False

    def getWinningTeams(self):
        '''
        Returns a set of all teams which have:
         (a) strict numerical advantage in this zone; or
         (b) more than 3 players in this zone.
        This takes into account the fact that turrets do not count towards
        numerical advantage.
        '''
        result = set()
        maxPlayers = 0
        for team, count in self.getPlayerCounts().iteritems():
            if maxPlayers > 3:
                if count > 3:
                    result.add(team)
            elif count > maxPlayers:
                result = set([team])
                maxPlayers = count
            elif count == maxPlayers:
                result = set()
        return result

    @staticmethod
    def canTag(numTaggers, numDefenders):
        '''
        Deprecated, do not use.
        '''
        return numTaggers > numDefenders or numTaggers > 3
