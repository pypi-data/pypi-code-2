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

import json
import logging

from trosnoth.utils.components import Component, Plug, handler
from trosnoth.messages import AddPlayerMsg, ChatMsg, JoinSuccessfulMsg
from trosnoth.model.universe_base import GameState
from trosnoth.utils.utils import timeNow

from trosnoth.gamerecording.achievementlist import (concreteAchievements,
        LeaderMultiKill, leaderAchievements, OncePerGame, OncePerTeamPerGame,
        stripPunctuation, getLeaderDescription)

log = logging.getLogger('achievements')

class PlayerAchievements(object):
    '''Tracks achievements for a single player.'''
    def __init__(self, player, world, outPlug):
        self.player = player
        self.world = world
        self.achievements = []
        self.achievementMap = {}

        for classType in concreteAchievements:
            if issubclass(classType, OncePerGame) or issubclass(classType,
                    OncePerTeamPerGame):
                pass
            else:
                self._addAchievement(classType(self.player, world, outPlug))

        for leaderName, achievementName in leaderAchievements.iteritems():
            self._addAchievement(LeaderMultiKill(self.player, world, outPlug,
                    leaderName, achievementName))

    def _addAchievement(self, achievement):
        self.achievements.append(achievement)
        for msgType in achievement.messages:
            self.achievementMap.setdefault(msgType, []).append(achievement)

    def gotMessage(self, msg):
        for achievement in self.achievementMap.get(msg.__class__, ()):
            if (mightApply(self.world, achievement) and
                    achievement.listeningForMessages()):
                achievement.processMessage(msg)

    def rejoined(self, player):
        self.player = player
        for achievement in self.achievements:
            achievement.rejoined(player)

    def saveProgress(self):
        if self.player.user is not None:
            self.player.user.saveProgressAchievements(self.achievements)

    def __str__(self):
        return str(self.achievements)

def mightApply(world, achievement):
    '''
    Returns True iff this achievement might apply, based on whether or not the
    game is on.
    '''
    if world.gameState == GameState.Ended:
        gameRunning = False
    elif world.gameState == GameState.InProgress:
        gameRunning = True
    else:
        return False

    return gameRunning ^ achievement.afterGame

class AchievementManager(Component):
    '''Listens for messages and triggers achievements accordingly.'''
    inPlug = Plug()
    outPlug = Plug()

    SAVE_PERIOD = 20

    def __init__(self, world, filename):
        Component.__init__(self)
        self.world = world
        self.filename = filename.replace('replace-this', 'players')
        self.metaFilename = filename.replace('replace-this', 'definitions')
        self.lastSave = timeNow()

        self._metaSave()

        # All players recorded this game, indexed by nick.
        self.allPlayers = {}

        self.oncePerGameAchievements = []
        self.oncePerTeamPerGameAchievements = []
        for classType in concreteAchievements:
            if issubclass(classType, OncePerGame):
                self.oncePerGameAchievements.append(classType(world,
                        self.outPlug))
            elif issubclass(classType, OncePerTeamPerGame):
                for team in world.teams:
                    self.oncePerTeamPerGameAchievements.append(classType(world,
                            team, self.outPlug))

    def _metaSave(self):
        '''Saves information about the achievements themselves to a JSON file.
        This is so the achievement info can be accessed by external applications
        (such as the camp website).'''

        allAchievements = {}

        for classType in concreteAchievements:
            if issubclass(classType, OncePerGame):
                allAchievements.update(classType(None, None).describe())
            else:
                allAchievements.update(classType(None, None, None).describe())

        for leaderName, achievementName in leaderAchievements.iteritems():
            idstring = 'leader' + stripPunctuation(leaderName)
            description = getLeaderDescription(leaderName)
            allAchievements.update({idstring: {'name': achievementName,
                                               'description': description,
                                               'type': 'incremental',
                                               'requirements': 3,
                                               'keepProgress': False}})

        file = open(self.metaFilename, 'w')
        jsonString = json.dumps(allAchievements, indent = 4)
        file.write(jsonString)
        file.flush()
        file.close()

    @inPlug.defaultHandler
    def passOn(self, msg):
        self._passMsgOn(msg)

    def _passMsgOn(self, msg):
        for achv in self.oncePerGameAchievements:
            if mightApply(self.world, achv) and not achv.unlocked:
                achv.processMessage(msg)
        for achv in self.oncePerTeamPerGameAchievements:
            if mightApply(self.world, achv) and not achv.unlocked:
                achv.processMessage(msg)
        for player in self.allPlayers.itervalues():
            player.gotMessage(msg)

        # We don't need to save like a madman with every message, so only save
        # the file every now and then.
        now = timeNow()
        if now - self.lastSave >= self.SAVE_PERIOD:
            self.lastSave = now
            self.save()

    def save(self):
        for playerAchievements in self.allPlayers.itervalues():
            playerAchievements.saveProgress()

    def stop(self):
        self.save()

    # Register on both AddPlayerMsg and JoinSuccessfulMsg because:
    # - First, AddPlayerMsg is sent before player.user is set.
    # - For reset games, JoinPlayerMsg is not sent, but player.user has been
    # set.
    @handler(AddPlayerMsg, inPlug)
    @handler(JoinSuccessfulMsg, inPlug)
    def addPlayer(self, msg):
        player = self.world.getPlayer(msg.playerId)
        name = player.identifyingName
        if name not in self.allPlayers:
            self.allPlayers[name] = (
                    PlayerAchievements(self.world.getPlayer(msg.playerId),
                    self.world, self.outPlug))
        else:
            self.allPlayers[name].rejoined(self.world.getPlayer(msg.playerId))

    @handler(ChatMsg, inPlug)
    def receieveChat(self, msg):
        # For Debugging
        if msg.text == ".":
            log.info(self.allPlayers[self.world.getPlayer(msg.playerId)
                    .identifyingName].achievements)
        self._passMsgOn(msg)

