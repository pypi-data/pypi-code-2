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

class Team(object):
    '''Represents a team of the game'''
    def __init__(self, world, teamID):
        self.world = world
        self.numOrbsOwned = 0

        self.captain = None
        self.ready = False
        self.minimapDisrupted = False

        if (not isinstance(teamID, str)) or len(teamID) != 1:
            raise TypeError, 'teamID must be a single character'
        self.id = teamID

        if teamID == "A":
            self.teamName = "Blue"
        else:
            self.teamName = "Red"

    def __repr__(self):
        return '%s team' % self.teamName

    def orbLost(self):
        '''Called when a orb belonging to this team has been lost'''
        self.numOrbsOwned -= 1

    def orbGained(self):
        '''Called when a orb has been attributed to this team'''
        self.numOrbsOwned += 1

    def isLoser(self):
        '''Returns whether the team has lost the game (True = Lost Game)'''
        return self.numOrbsOwned == 0

    def canSetCaptain(self):
        return self.captain == None

    def setCaptain(self, player):
        assert(self.canSetCaptain())
        assert(player.team == self)
        self.captain = player

    def teamReady(self):
        self.ready = True

    def playerHasLeft(self, player):
        if self.captain == player:
            self.captain = None
            self.ready = False

    @staticmethod
    def setOpposition(teamA, teamB):
        teamA.opposingTeam = teamB
        teamB.opposingTeam = teamA
