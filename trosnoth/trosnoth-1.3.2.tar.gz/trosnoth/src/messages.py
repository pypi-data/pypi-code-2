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

from trosnoth.src.network.netmsg import NetworkMessage
from trosnoth.src.utils.components import Message

####################
# Chat
####################

class ChatFromServerMsg(NetworkMessage):
    idString = 'ahoy'
    fields = 'text'
    packspec = '*'

class ChatMsg(NetworkMessage):
    '''
    kind may be 't' for team, 'p' for private, 'o' for open.
    '''
    idString = 'chat'
    fields = 'playerId', 'kind', 'targetId', 'text'
    packspec = 'ccc*'

####################
# Gameplay
####################

class TaggingZoneMsg(NetworkMessage):
    idString = 'Tag!'
    fields = 'zoneId', 'playerId', 'teamId'
    packspec = 'Icc'

class KilledMsg(NetworkMessage):
    idString = 'Dead'
    fields = 'targetId', 'killerId', 'shotId', 'xPos', 'yPos'
    packspec = 'cccff'

class KillShotMsg(NetworkMessage):
    idString = 'KiSh'
    fields = 'shooterId', 'shotId'
    packspec = 'cc'

class PlayerUpdateMsg(NetworkMessage):
    idString = 'PlUp'
    fields = ('playerId', 'xPos', 'yPos', 'yVel', 'angle', 'ghostThrust',
            'keys')
    packspec = 'cfffff*'

class RespawnMsg(NetworkMessage):
    idString = 'Resp'
    fields = 'playerId', 'zoneId'
    packspec = 'cI'

class RespawnRequestMsg(NetworkMessage):
    idString = 'Resp'
    fields = 'playerId', 'tag'
    packspec = 'cI'

class CannotRespawnMsg(NetworkMessage):
    idString = 'NoRs'
    fields = 'playerId', 'reasonId', 'tag'
    packspec = 'ccI'

class PlayerKilledMsg(NetworkMessage):
    idString = 'Dead'
    fields = 'targetId', 'killerId', 'shotId'
    packspec = 'ccc'

class PlayerHitMsg(NetworkMessage):
    idString = 'PlHt'
    fields = 'targetId', 'shooterId', 'shotId'
    packspec = 'ccc'

####################
# Game
####################

class SetCaptainMsg(NetworkMessage):
    idString = 'CapN'
    fields = 'playerId'
    packspec = 'c'
    
class TeamIsReadyMsg(NetworkMessage):
    idString = 'Redy'
    fields = 'playerId'
    packspec = 'c'

class GameStartMsg(NetworkMessage):
    idString = 'Go!!'
    fields = 'timeLimit'
    packspec = 'd'

class GameOverMsg(NetworkMessage):
    idString = 'Stop'
    fields = 'teamId', 'timeOver'
    packspec = 'cB'

class SetGameModeMsg(NetworkMessage):
    idString = 'Mode'
    fields = 'gameMode'
    packspec = '*'

class SetTeamNameMsg(NetworkMessage):
    idString = 'Team'
    fields = 'teamId', 'name'
    packspec = 'c*'

class StartingSoonMsg(NetworkMessage):
    idString = 'Wait'
    fields = 'delay'
    packspec = 'd'

####################
# Players
####################

class JoinRequest(Message):
    fields = 'team', 'nick'

class AddPlayerMsg(NetworkMessage):
    idString = 'NewP'
    fields = 'playerId', 'teamId', 'zoneId', 'dead', 'nick'
    packspec = 'ccIb*'

class RemovePlayerMsg(NetworkMessage):
    idString = 'DelP'
    fields = 'playerId'
    packspec = 'c'

class JoinRequestMsg(NetworkMessage):
    idString = 'Join'
    fields = 'teamId', 'tag', 'nick'
    packspec = 'cI*'

class JoinApproved(Message):
    '''
    Validator talking to id manager.
    '''
    fields = 'teamId', 'tag', 'zoneId', 'nick'

class CannotJoinMsg(NetworkMessage):
    idString = 'NotP'
    fields = 'reasonId', 'teamId', 'tag', 'waitTime'
    packspec = 'ccIf'
    waitTime = 0 # Default value.

class JoinSuccessfulMsg(NetworkMessage):
    idString = 'OwnP'
    fields = 'playerId', 'tag'
    packspec = 'cI'

class UpdatePlayerStateMsg(NetworkMessage):
    idString = 'Pres'
    fields = 'playerId', 'value', 'stateKey'
    packspec = 'cb*'

class AimPlayerAtMsg(NetworkMessage):
    idString = 'Aim@'
    fields = 'playerId', 'angle', 'thrust'
    packspec = 'cff'

####################
# Setup
####################

class InitClientMsg(NetworkMessage):
    idString = 'wlcm'
    fields = 'settings'
    packspec = '*'

class ConnectionLostMsg(Message):
    fields = ()

class QueryWorldParametersMsg(NetworkMessage):
    idString = 'What'
    fields = 'tag',
    packspec = 'I'

class SetWorldParametersMsg(NetworkMessage):
    idString = 'Set.'
    fields = 'tag', 'settings'
    packspec = 'I*'

class RequestMapBlockLayoutMsg(NetworkMessage):
    idString = 'RqMB'
    fields = 'tag', 'key'
    packspec = 'I*'

class MapBlockLayoutMsg(NetworkMessage):
    idString = 'MapB'
    fields = 'tag', 'data'
    packspec = 'I*'

class RequestPlayersMsg(NetworkMessage):
    idString = 'RqPl'
    fields = ()
    packspec = ''

class RequestZonesMsg(NetworkMessage):
    idString = 'RqZn'
    fields = ()
    packspec = ''

class ZoneStateMsg(NetworkMessage):
    idString = 'ZnSt'
    fields = 'zoneId', 'teamId', 'dark'
    packspec = 'Icb'

####################
# Shot
####################

class ShootMsg(NetworkMessage):
    '''
    agent -> validator
    '''
    idString = 'shot'
    fields = 'playerId'
    packspec = 'c'

class FireShotMsg(NetworkMessage):
    '''
    validator -> id manager
    '''
    idString = 'shot'
    fields = 'playerId', 'angle', 'xpos', 'ypos', 'type'
    packspec = 'cfffc'

class ShotFiredMsg(NetworkMessage):
    '''
    id manager -> agents
    '''
    idString = 'SHOT'
    fields = 'playerId', 'shotId', 'angle', 'xpos', 'ypos', 'type'
    packspec = 'ccfffc'

####################
# Upgrades
####################

class DeleteUpgradeMsg(NetworkMessage):
    idString = 'DUpg'
    fields = 'playerId', 'upgradeType'
    packspec = 'cc'

class BuyUpgradeMsg(NetworkMessage):
    '''
    Signal from interface that a buy has been requested.

    Tag is an arbitrary integer which is returned in PlayerHasUpgradeMsg or
    PlayerStarsSpentMsg to indicate the request to which this response is being
    made.
    '''
    idString = 'GetU'
    fields = 'playerId', 'upgradeType', 'tag'
    packspec = 'ccI'

class PlayerHasUpgradeMsg(NetworkMessage):
    '''
    Signal from validator that the player now has the specified upgrade.
    Recipients of this message should not decrement player star counts except
    due to receipt of a PlayerStarsSpentMsg.
    '''
    idString = 'GotU'
    fields = 'playerId', 'upgradeType'
    packspec = 'cc'

class PlayerStarsSpentMsg(NetworkMessage):
    idString = 'Spnt'
    fields = 'playerId', 'count'
    packspec = 'cI'

class CannotBuyUpgradeMsg(NetworkMessage):
    '''
    Tag is the value sent in BuyUpgradeMsg.
    reasonId may be:
        'N' - not enough stars
        'A' - already have upgrade
        'D' - player is dead
        'P' - game has not yet started
        'T' - there's already a turret in the zone
        'E' - too close to zone edge
        'O' - too close to orb
        'F' - not in a dark friendly zone
        'M' - your team has a minimap disruption in use
    '''
    idString = 'NotU'
    fields = 'playerId', 'reasonId', 'tag'
    packspec = 'ccI'

############################
# Connection
############################

class RequestUDPStatusMsg(NetworkMessage):
    idString = 'rUDP'
    fields = ()
    packspec = ''

class NotifyUDPStatusMsg(NetworkMessage):
    idString = 'vUDP'
    fields = 'connected'
    packspec = 'b'

############################
# Message Collections
############################

tcpMessages = set([
    ChatFromServerMsg,
    ChatMsg,
    GameStartMsg,
    GameOverMsg,
    SetGameModeMsg,
    SetTeamNameMsg,
    StartingSoonMsg,
    AddPlayerMsg,
    RemovePlayerMsg,
    JoinSuccessfulMsg,
    CannotJoinMsg,
    InitClientMsg,
    QueryWorldParametersMsg,
    SetWorldParametersMsg,
    RequestMapBlockLayoutMsg,
    MapBlockLayoutMsg,
    RequestPlayersMsg,
    RequestZonesMsg,
    ZoneStateMsg,
    RequestUDPStatusMsg,
    NotifyUDPStatusMsg,
    PlayerHasUpgradeMsg,
])
