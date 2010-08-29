# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2007  Joshua Bartlett
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

'''leaderboard.py - defines the LeaderBoard class which deals with drawing the
leader board to the screen.'''

import pygame
from twisted.internet import reactor
import struct

from trosnoth.data import getPath, sprites
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.gui.common import (Location, ScaledScalar,
        FullScreenAttachedPoint, SizedImage, ScaledSize)
from trosnoth.src.gui.framework import table
from trosnoth.src.gui.framework.elements import PictureElement
from trosnoth.src.model.universe_base import GameState

# How often the leaderboard will update (in seconds)
UPDATE_DELAY = 1.0

class LeaderBoard(framework.CompoundElement):
    
    def __init__(self, app, world, gameViewer):
        super(LeaderBoard, self).__init__(app)
        self.world = world
        self.gameViewer = gameViewer
        self.app = app
        self.scale = self.app.screenManager.scaleFactor

        self.xPos = 4
        self.yPos = self.gameViewer.miniMap.getRect().bottom + self.gameViewer.zoneBarHeight + 5
        position = Location(FullScreenAttachedPoint((self.xPos, self.yPos), 'topright'), 'topright')

        # Create the table and set all the appropriate style attributes
        self.playerTable = table.Table(app, position, columns = 3)

        self.playerTable.setBorderWidth(0)
        self.playerTable.setBorderColour((0, 0, 0))

        self.playerTable.style.backColour = None
        self.playerTable.style.foreColour = app.theme.colours.leaderboardNormal
        self.playerTable.style.font = self.app.screenManager.fonts.leaderboardFont
        self.playerTable.style.padding = (4, 1)
        self.playerTable.style.hasShadow = True
        self.playerTable.style.shadowColour = (0, 0, 0)
        
        self.playerTable.getColumn(0).style.textAlign = 'midright'
        self.playerTable.getColumn(1).style.textAlign = 'center'
        self.playerTable.getColumn(2).style.textAlign = 'midleft'

        self.rowHeight = 25

        self.playerTable.getColumn(0).setWidth(ScaledScalar(150))   # Name column
        self.playerTable.getColumn(1).setWidth(ScaledScalar(25))    # Star column
        self.playerTable.getColumn(2).setWidth(ScaledScalar(70))    # Upgrade column

        self.colourLookup = {"A": app.theme.colours.leaderboardBlue,
                "B": app.theme.colours.leaderboardRed}

        self._resetPlayers()

        self.elements = [self.playerTable]
        self.update(True)

    def _resetPlayers(self):
        self.players = {"A": [], "B": []}

    def update(self, loop=False):
        self._resetPlayers()

        if self.world.gameState == GameState.InProgress:
            yPos = self.yPos
        else:
            yPos = self.yPos + int(50 * self.scale)
        self.playerTable.pos = Location(FullScreenAttachedPoint((self.xPos, yPos), 'topright'), 'topright')         

        try:
            self.friendlyTeam = self.gameViewer.interface.runningPlayerInterface.player.team
            self.enemyTeam = self.friendlyTeam.opposingTeam
            self.spectator = False
        except AttributeError:
            # This will occur if the player is not yet on a team
            self.friendlyTeam = self.world.teamWithId["A"]
            self.enemyTeam = self.world.teamWithId["B"]
            self.spectator = True

        for player in self.world.players:
            # getDetails() returns dict with pID, nick, team, dead, stars, upgrade
            details = player.getDetails()
            self.players[details["team"]].append(details)
    
        self._sort("A")
        self._sort("B")
        self._updateTable()

        if loop:
            self.callDef = reactor.callLater(UPDATE_DELAY, self.update, True)

    def _sort(self, team):

        starList = []
        sortedList = []
        teamPlayers = self.players[team][:]

        for details in teamPlayers:
            if details["dead"]:
                sortedList.append(details)
            else:
                starList.append(details["stars"])
                starList.sort()
                starList.reverse()
                
                sortedList.insert(starList.index(details["stars"]), details)
                
        # List is now sorted with dead people at the bottom and the alive people
        # in order of stars.

        self.players[team] = sortedList[:]

    def _updateTable(self):
        for x in range(self.playerTable.rowCount()):
            self.playerTable.delRow(0)

        count = -1
        self.indexes = {}

        shortNames = {"Minimap Disruption": "minimap",
                      "Phase Shift": "phase"}

        # Upgrades that the enemy team have that you are allowed to see
        visibleUpgrades = ["Minimap Disruption", "Turret"]
        # Upgrades that are currently in use that you are allowed to see
        visibleInUse = visibleUpgrades + ["Shield", "Grenade"]

        for team, players in [(self.friendlyTeam, self.players[self.friendlyTeam.id]),
                              (self.enemyTeam, self.players[self.enemyTeam.id])]:

            # Add the team header
            if len(players) > 0:
                count += 1
                self.playerTable.addRow()
                self.playerTable.getRow(count).setHeight(ScaledScalar(self.rowHeight))
                self.playerTable[0][count].setText(team.teamName + " team")

                if self.world.gameState == GameState.InProgress:
                    starImage = SizedImage(getPath(sprites, 'smallstar.png'), ScaledSize(14, 13), (255,255,255))
                    xPos = int(1 * self.scale)
                    yPos = int(5 * self.scale)
                    starImage = PictureElement(self.app, starImage,
                                               Location(table.CellAttachedPoint((xPos,yPos), self.playerTable[1][count], 'topleft')))
                    self.playerTable[1][count].elements = [starImage]

                    if len(players) == 1:
                        noun = "player"
                    else:
                        noun = "players"
                    self.playerTable[2][count].setText(str(len(players)) + " " + noun)
                else:
                    self.playerTable[1][count].elements = []

                if self.world.gameState in (GameState.PreGame,
                        GameState.Starting):
                    if team.ready:
                        self.playerTable[2][count].setText("ready")
                        self.playerTable[2][count].style.foreColour = \
                                self.app.theme.colours.leaderboardNormal
                    else:
                        self.playerTable[2][count].setText("not ready")
                        self.playerTable[2][count].style.foreColour = \
                                self.app.theme.colours.leaderboardDead
                elif self.world.gameState == GameState.Ended:
                    if self.world.winningTeam == team:
                        self.playerTable[2][count].setText("has won!")
                    elif self.world.winningTeam is not None:
                        self.playerTable[2][count].setText("has lost.")
                    else:
                        self.playerTable[2][count].setText("has drawn!")
                    self.playerTable[2][count].style.foreColour = self.colourLookup[team.id]

                self.playerTable.getRow(count).style.foreColour = self.colourLookup[team.id]
                self.indexes["header"+team.id] = count
                
            # Add a row for each player   
            for player in players:
                count += 1
                self.playerTable.addRow()
                self.playerTable.getRow(count).setHeight(ScaledScalar(self.rowHeight))
                self.playerTable[0][count].setText(player["nick"])

                if self.world.gameState in (GameState.PreGame,
                        GameState.Starting):
                    if team.captain is not None:
                        if player["pID"] == struct.unpack('B', team.captain.id)[0]:
                            self.playerTable[2][count].setText("captain")
                else:
                    # Don't show enemy stars
                    if team is self.friendlyTeam or self.spectator:
                        self.playerTable[1][count].setText(str(player["stars"]))

                        
                    if player["upgrade"] is None:
                        upgradeText = ""
                    else:

                        # Check if the upgrade is in the appropriate whitelist.
                        # If there's an easier way of checking this, I haven't found it.                        
                        if team is self.enemyTeam and ((player["upgradeInUse"] and player["upgrade"] not in visibleInUse) \
                                                        or (not player["upgradeInUse"] and player["upgrade"] not in visibleUpgrades)):
                            upgradeText = ""
                        else:
                            # Use the short upgrade name if necessary
                            if player["upgrade"] in shortNames:
                                upgradeText = "+ " + shortNames[player["upgrade"]]
                            else:
                                upgradeText = "+ " + player["upgrade"].lower()
                        
                    self.playerTable[2][count].setText(upgradeText)
                    if player["upgradeInUse"]:
                        self.playerTable[2][count].style.foreColour = \
                                self.app.theme.colours.leaderboardNormal
                    else:
                        self.playerTable[2][count].style.foreColour = \
                                self.app.theme.colours.leaderboardDead

                if player["dead"]:
                    self.playerTable[0][count].style.foreColour = \
                            self.app.theme.colours.leaderboardDead
                    self.playerTable[1][count].style.foreColour = \
                            self.app.theme.colours.leaderboardDead
                else:
                    self.playerTable[0][count].style.foreColour = \
                            self.colourLookup[team.id]
                    self.playerTable[1][count].style.foreColour = \
                            self.app.theme.colours.leaderboardNormal

            # Add the "star total" row
            if (len(players) > 1 and self.world.gameState not in
                    (GameState.PreGame, GameState.Starting)):
                count += 1
                self.playerTable.addRow()
                self.playerTable.getRow(count).setHeight(ScaledScalar(self.rowHeight))
                self.playerTable[0][count].setText("Total:")
                teamStars = self.world.getTeamStars(team)
                self.playerTable[1][count].setText(teamStars)
                if teamStars == 1:
                    noun = "star"
                else:
                    noun = "stars"
                self.playerTable[2][count].setText(noun)
                self.indexes["total"+team.id] = count
        
    def kill(self):
        self.callDef.cancel()

    def draw(self, surface):
        super(LeaderBoard, self).draw(surface)

        # pointA = left-most point of the line
        # pointB = right-most point of the line
        # pointC = left-most point of the line shadow
        # pointD = right-most point of the line shadow

        for name, index in self.indexes.iteritems():
            if name[:6] == 'header':
                rightMargin = int(8 * self.scale)
                leftMargin = int(40 * self.scale)
                bottomMargin = int(2 * self.scale)
                
                point = self.playerTable._getRowPt(index + 1)
                pointA = (point[0] + leftMargin, point[1] - bottomMargin)
                pointB = (pointA[0] + self.playerTable._getSize()[0] - leftMargin - rightMargin, pointA[1])
                pointC, pointD = shift(pointA, pointB)
                pygame.draw.line(surface, self.colourLookup[name[-1:]], pointA, pointB, 1)
                pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

                pointA, pointB = shift(pointA, pointB, -self.playerTable.getRow(index)._getHeight() + bottomMargin, 0)
                pointC, pointD = shift(pointA, pointB)
                pygame.draw.line(surface, self.colourLookup[name[-1:]], pointA, pointB, 1)
                pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

            if name[:5] == 'total':
                bottomMargin = int(2 * self.scale)

                rowPoint = self.playerTable._getRowPt(index)
                colPoint = self.playerTable._getColPt(1)
                pointA = (colPoint[0], rowPoint[1] - bottomMargin)
                pointB = (pointA[0] + self.playerTable.getColumn(1)._getWidth(), pointA[1])
                pointC, pointD = shift(pointA, pointB)
                pygame.draw.line(surface,
                        self.app.theme.colours.leaderboardNormal, pointA,
                        pointB, 1)
                pygame.draw.line(surface, (0, 0, 0), pointC, pointD, 1)

def shift(pointA, pointB, down = 1, right = 1):
    '''Returns two points that are shifted by the specified number of pixels.
    Negative values shift up and left, positive values shift down and right.'''
    return ((pointA[0] + right, pointA[1] + down),
            (pointB[0] + right, pointB[1] + down))
                
