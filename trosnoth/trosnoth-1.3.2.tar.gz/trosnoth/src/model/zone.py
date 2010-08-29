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

from trosnoth.src.utils.logging import writeException

class ZoneDef(object):
    '''Stores static information about the zone.

    Attributes:
        adjacentZones - mapping from adjacent ZoneDef objects to collection of
            map blocks joining the zones.
        id - the zone id (TODO: remove the need for this at this level)
        initialOwner - the team that initially owned this zone,
            represented as a number (0 for neutral, 1 or 2 for a team).
        pos - the coordinates of this zone in the map
    '''
    def __init__(self, id, initialOwnerIndex, xCoord, yCoord):
        self.adjacentZones = {}
        self.id = id
        self.initialOwnerIndex = initialOwnerIndex
        self.pos = xCoord, yCoord

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

class ZoneState(object):
    '''Represents information about a given zone and its state.

    Attributes:
        universe
        zoneOwner - a team
        orbOwner - a team
        players - a Group
        nonPlayers - a Group for ghosts
        taggedThisTime - boolean flag used to compare whether multiple players have tagged the zone in one tick
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

        self.players = set()

        # zone.nonPlayers are those players that do not count in zone
        # calculations, such as ghosts and decoys
        self.nonPlayers = set()
        self.taggedThisTime = False
        self.turretedPlayer = None

    def __str__(self):
        # Debug: uniquely identify this zone within the universe.
        if self.id == None:
            return 'Z---'
        return 'Z%3d' % self.id

    def tag(self, player):
        '''This method should be called when the orb in this zone is tagged'''
        # Inform the team objects
        if self.orbOwner:
            self.orbOwner.orbLost()
        if player is not None:
            team = player.team
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

    def setOwnership(self, team, dark):
        if self.orbOwner is not None:
            self.orbOwner.orbLost()
        self.orbOwner = team
        if team is not None:
            team.orbGained()
        if dark:
            self.zoneOwner = team
        else:
            self.zoneOwner = None

    def checkAgain(self):
        '''This method should be called by an adjacent friendly zone that has
        been tagged and gained. It will check to see if it now has all
        surrounding orbs owned by the same team, in which case it will
        change its zone ownership.'''

        # If the zone is already owned, ignore it
        if self.zoneOwner != self.orbOwner and self.orbOwner != None:
            for zoneDef in self.defn.adjacentZones:
                zone = self.universe.zoneWithDef[zoneDef]
                if zone.orbOwner == self.orbOwner \
                   or zone.orbOwner == None:
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
                distance = ((xCoord1 - xCoord2) ** 2 + \
                            (yCoord1 - yCoord2) ** 2) ** 0.5
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
        except KeyError:
            writeException()

    def addPlayer(self, player):
        '''Adds a player to this zone'''
        try:
            if player.ghost:
                if player not in self.nonPlayers:
                    self.nonPlayers.add(player)
            else:
                if player not in self.players:
                    self.players.add(player)
        except KeyError:
            writeException()
