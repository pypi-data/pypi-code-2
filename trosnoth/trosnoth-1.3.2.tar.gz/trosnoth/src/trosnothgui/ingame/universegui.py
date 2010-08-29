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

'''
Provides a layer between a universe and the GUI, turning
players, shots, grenades into sprites, and drawing mapblocks.
'''

from trosnoth.src.trosnothgui.ingame.sprites import PlayerSprite, ShotSprite, GrenadeSprite

class UniverseGUI(object):
    def __init__(self, app, universe):
        self.app = app
        self.universe = universe
        # Sprites
        self.playerSprites = {}     # playerId -> PlayerSprite
        self.shotSprites = {}       # (playerId, shotId) -> PlayerSprite
        self.grenadeSprites = {}    # playerId -> GrenadeSprite

    @property
    def zones(self):
        return self.universe.zones

    @property
    def map(self):
        return self.universe.map

    @property
    def zoneBlocks(self):
        return self.universe.zoneBlocks
        
    def getPlayerSprite(self, playerId):
        try:
            return self.playerSprites[playerId]
        except KeyError:
            return None

    def iterPlayers(self):
        untouched = set(self.playerSprites.iterkeys())
        for player in self.universe.players:
            try:
                yield self.playerSprites[player.id]
            except KeyError:
                self.playerSprites[player.id] = p = PlayerSprite(self.app,
                        player)
                yield p
            else:
                untouched.discard(player.id)

        # Clean up old players.
        for playerId in untouched:
            del self.playerSprites[playerId]

    def iterGrenades(self):
        untouched = set(self.grenadeSprites.iterkeys())
        for grenade in self.universe.grenades:
            try:
                yield self.grenadeSprites[grenade.id]
            except KeyError:
                self.grenadeSprites[grenade.id] = g = GrenadeSprite(self.app,
                        grenade)
                yield g
            else:
                untouched.discard(grenade.id)

        # Clean up old players.
        for grenadeId in untouched:
            del self.grenadeSprites[grenadeId]

    def iterShots(self):
        untouched = set(self.shotSprites.iterkeys())
        for shot in self.universe.shots:
            try:
                yield self.shotSprites[shot.originatingPlayer.id, shot.id]
            except KeyError:
                self.shotSprites[shot.originatingPlayer.id, shot.id] = s = (
                        ShotSprite(self.app, shot))
                yield s
            else:
                untouched.discard((shot.originatingPlayer.id, shot.id))

        # Clean up old shots.
        for playerId, shotId in untouched:
            del self.shotSprites[playerId, shotId]

    def getPlayerCount(self):
        return len(self.universe.players)

    def hasPlayer(self, playerSprite):
        return playerSprite.player.id in self.playerSprites

    def getPlayersInZone(self, zone):
        result = []
        for p in list(zone.players) + list(zone.nonPlayers):
            ps = self.getPlayerSprite(p.id)
            if ps is not None:
                result.append(ps)
        return result

    def addPlayer(self, player):
        self.playerSprites[player.id] = PlayerSprite(self.app, player)

    def removePlayer(self, player):
        try:
            del self.playerSprites[player.id]
        except KeyError:
            pass

    def addShot(self, shot):
        self.shotSprites[shot.originatingPlayer.id, shot.id] = ShotSprite(
                self.app, shot)

    def removeShot(self, playerId, shotId):
        try:
            del self.shotSprites[playerId, shotId]
        except KeyError:
            pass

    def addGrenade(self, grenade):
        self.grenadeSprites[grenade.player.id] = GrenadeSprite(self.app,
                grenade)

    def removeGrenade(self, grenade):
        try:
            del self.grenadeSprites[grenade.player.id]
        except KeyError:
            pass

    def tick(self, deltaT):
        for player in self.iterPlayers():
            player.update()
        for shot in self.iterShots():
            shot.update()
        for grenade in self.iterGrenades():
            grenade.update()
