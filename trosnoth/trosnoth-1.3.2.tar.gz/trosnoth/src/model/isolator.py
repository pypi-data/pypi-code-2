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

import random
from trosnoth.src.model.universe import Universe
from trosnoth.src.model.map import MapLayout
from trosnoth.src.messages import (AddPlayerMsg, QueryWorldParametersMsg,
        SetWorldParametersMsg, RequestMapBlockLayoutMsg, MapBlockLayoutMsg,
        RequestPlayersMsg, PlayerUpdateMsg, RequestZonesMsg, SetCaptainMsg,
        ZoneStateMsg, PlayerHasUpgradeMsg, TeamIsReadyMsg)
from trosnoth.src.utils.components import (Component, Plug, queueMessage,
        handler)
from trosnoth.src.utils.unrepr import unrepr
from twisted.internet import reactor

TIMEOUT = 5

class Isolator(Component):
    '''
    This component is designed to sit between an agent and a game engine in the
    case where the agent can't see the game engine's actual world. The isolator
    creates a world which reflects the game engine's world by sending
    appropriate query messages.
    '''

    # agentEvents <- Isolator <- gameEvents
    gameEvents = Plug()
    agentEvents = Plug()

    # agentRequests -> Isolator -> gameRequests
    agentRequests = Plug()
    gameRequests = Plug()

    def __init__(self, layoutDatabase):
        Component.__init__(self)
        self.world = Universe()
        self.world.replay = False
        self.layoutDatabase = layoutDatabase
        self.gotParams = False
        self.unknownKeys = None
        self.mapSpec = None
        self.timer = None
        self.paramPassTags = {}
        self.blockPassTags = {}

    def begin(self):
        '''
        Instructs this isolator to begin getting the world information from the
        server.
        '''
        self.gameRequests.send(QueryWorldParametersMsg(random.randrange(1<<32)))

    @handler(QueryWorldParametersMsg, agentRequests)
    def gotParamsQueryFromAgent(self, msg):
        self.paramPassTags[msg.tag] = reactor.callLater(TIMEOUT,
                self._discardParamTag, msg.tag)

    def _discardParamTag(self, tag):
        if tag in self.paramPassTags:
            del self.paramPassTags[tag]

    @handler(SetWorldParametersMsg, gameEvents)
    def gotWorldParams(self, msg):
        if msg.tag in self.paramPassTags:
            # The request was sent from further downstream.
            self.paramPassTags[msg.tag].cancel()
            del self.paramPassTags[msg.tag]
            self.agentEvents.send(msg)

        data = unrepr(msg.settings)
        self.mapSpec = mapSpec = data.pop('worldMap')
        self.world.applyWorldParameters(data)

        self.gotParams = True
        keys = MapLayout.unknownBlockKeys(self.layoutDatabase, mapSpec)
        self.unknownKeys = keys
        if len(keys) == 0:
            self._applyMapLayout()
        else:
            self._sendBlockRequests()

    def _applyMapLayout(self):
        layout = MapLayout.fromString(self.layoutDatabase, self.mapSpec)
        self.world.setLayout(layout)
        self._requestPlayers()
        self._requestZoneOwners()

    def _requestPlayers(self):
        self.gameRequests.send(RequestPlayersMsg())

    def _requestZoneOwners(self):
        self.gameRequests.send(RequestZonesMsg())

    def _sendBlockRequests(self):
        '''
        Sends the world requests for the map blocks unknown by our layout
        database.
        '''
        for key in self.unknownKeys:
            self.gameRequests.send(RequestMapBlockLayoutMsg(
                    random.randrange(1<<32), repr(key)))

    @handler(RequestMapBlockLayoutMsg, agentRequests)
    def gotBlockQueryFromAgent(self, msg):
        self.blockPassTags[msg.tag] = reactor.callLater(TIMEOUT,
                self._discardBlockTag, msg.tag)

    def _discardBlockTag(self, tag):
        if tag in self.blockPassTags:
            del self.blockPassTags[tag]

    @handler(MapBlockLayoutMsg, gameEvents)
    def gotMapBlock(self, msg):
        if msg.tag in self.blockPassTags:
            # Request came from further downstream.
            self.blockPassTags[msg.tag].cancel()
            del self.blockPassTags[msg.tag]
            self.agentEvents.send(msg)

        key, contents, graphics = unrepr(msg.data)
        self.layoutDatabase.addDownloadedBlock(key, contents, graphics)
        self.unknownKeys.remove(key)
        if len(self.unknownKeys) == 0:
            self._applyMapLayout()

    @handler(PlayerUpdateMsg, gameEvents)
    def gotPlayerUpdate(self, msg):
        queueMessage(self.world.orderPlug, msg)
        self.agentEvents.send(msg)

    @gameEvents.defaultHandler
    def passToAgent(self, msg):
        queueMessage(self.world.orderPlug, msg)
        self.agentEvents.send(msg)

    @agentRequests.defaultHandler
    def passToGame(self, msg):
        self.gameRequests.send(msg)

class WorldSettingsResponder(Component):
    '''
    This component is designed to sit between an agent and a game engine in the
    case where the world is a local world, and respond to requests from the
    isolator.
    '''

    # agentEvents <- Isolator <- gameEvents
    gameEvents = Plug()
    agentEvents = Plug()

    # agentRequests -> Isolator -> gameRequests
    agentRequests = Plug()
    gameRequests = Plug()

    def __init__(self, world, layoutDatabase):
        Component.__init__(self)
        self.world = world
        self.layoutDatabase = layoutDatabase

    @gameEvents.defaultHandler
    def passToAgent(self, msg):
        self.agentEvents.send(msg)

    @agentRequests.defaultHandler
    def passToGame(self, msg):
        self.gameRequests.send(msg)

    @handler(QueryWorldParametersMsg, agentRequests)
    def queryWorldParams(self, msg):
        data = self.world._getWorldParameters()
        data['worldMap'] = self.world.map.layout.toString()
        self.agentEvents.send(SetWorldParametersMsg(msg.tag,
                repr(data)))

    @handler(RequestMapBlockLayoutMsg, agentRequests)
    def queryMapBlock(self, msg):
        key = unrepr(msg.key)
        layout = self.layoutDatabase.getLayoutByKey(key)
        if layout is None:
            # We do not know the key.
            contents = None
            graphics = None
        else:
            contents = open(layout.filename, 'rU').read()
            graphics = layout.getGraphicsData()
        data = (key, contents, graphics)
        self.agentEvents.send(MapBlockLayoutMsg(msg.tag, repr(data)))

    @handler(RequestPlayersMsg, agentRequests)
    def queryPlayers(self, msg):
        for player in self.world.players:
            self.agentEvents.send(AddPlayerMsg(player.id, player.team.id,
                    player.currentZone.id, player.ghost, player.nick.encode()))
            self.agentEvents.send(player.makePlayerUpdate())
        for team in self.world.teams:
            if team.captain is not None:
                self.agentEvents.send(SetCaptainMsg(team.captain.id))
                if team.ready:
                    self.agentEvents.send(TeamIsReadyMsg(team.captain.id))
        self.queryUpgrades()

    @handler(RequestZonesMsg, agentRequests)
    def queryZones(self, msg):
        for zone in self.world.zones:
            if zone.orbOwner is None:
                owner = '\x00'
            else:
                owner = zone.orbOwner.id
            dark = zone.zoneOwner != None
            self.agentEvents.send(ZoneStateMsg(zone.id, owner, dark))

    def queryUpgrades(self):
        for player in self.world.players:
            if player.upgrade is not None:
                self.agentEvents.send(PlayerHasUpgradeMsg(player.id,
                        player.upgrade.upgradeType))
