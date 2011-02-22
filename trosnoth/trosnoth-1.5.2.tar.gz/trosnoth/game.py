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

from email.mime.text import MIMEText
import logging
import random

from trosnoth.ai import makeAIAgent, listAIs
from trosnoth.model.universe import Universe
from trosnoth.model.idmanager import IdManager
from trosnoth.model.validator import Validator
from trosnoth.model.agentfilter import AgentFilter
from trosnoth.model.universe_base import GameState
from trosnoth.model.isolator import Isolator, WorldSettingsResponder
from trosnoth.messages import (SetTeamNameMsg, GameStartMsg, GameOverMsg,
        SetGameModeMsg, RemovePlayerMsg, PlayerHasUpgradeMsg,
        SetGameSpeedMsg)
from trosnoth.gamerecording.gamerecorder import makeGameRecorder
from trosnoth.utils.twist import WeakLoopingCall

log = logging.getLogger('game')

def makeLocalGame(gameName, layoutDatabase, halfMapWidth, mapHeight, duration=0,
        maxPlayers=8, authTagManager=None, voting=False, alertSettings=None,
        onceOnly=False, bootServer=True):
    '''
    Makes and returns a local game.
    layoutDatabase may be a LayoutDatabase, or None. If None, the game will not
    be queryable by remote games.
    '''
    alerter = Alerter(alertSettings)
    idManager = IdManager()
    world = Universe(gameDuration=duration, authTagManager=authTagManager,
            voting=voting, layoutDatabase=layoutDatabase, gameName=gameName,
            onceOnly=onceOnly)
    validator = Validator(world, maxPlayers, authTagManager, alerter=alerter)

    world.eventPlug.connectPlug(idManager.inPlug)
    world.orderPlug.connectPlug(idManager.outPlug)
    validator.gameRequests.connectPlug(idManager.inPlug)
    validator.gameEvents.connectPlug(idManager.outPlug)

    gameRecorder = makeGameRecorder(world, layoutDatabase, idManager)

    if layoutDatabase is None:
        game = Game(world, validator.agentEvents, validator.agentRequests,
                gameRecorder, bootServer=bootServer)
    else:
        game = QueryableGame(world, validator.agentEvents,
                validator.agentRequests, gameRecorder, layoutDatabase,
                bootServer=bootServer)
    layout = layoutDatabase.generateRandomMapLayout(halfMapWidth, mapHeight)
    world.setLayout(layout)
    gameRecorder.begin()
    return game

def makeIsolatedGame(layoutDatabase):
    '''
    Returns game, eventPlug, controller where game is a Game object and
    eventPlug and controller are plugs which allow this game to be connected
    into another game as an agent.

    This is here to test that having separate universes talking to each other
    works, without having to set up a server over the network.
    '''
    game = IsolatedGame(layoutDatabase)

    return game, game.eventPlug, game.requestPlug

class Game(object):
    def __init__(self, world, outPlug, inPlug, gameRecorder, bootServer=False):
        self.world = world
        self._outPlug = outPlug
        self._inPlug = inPlug
        self.gameRecorder = gameRecorder
        if bootServer:
            self.aiInjector = AIInjector(self)
        else:
            self.aiInjector = None

    @property
    def name(self):
        return self.world.gameName

    def addAgent(self, eventPlug, controller):
        '''
        Connects an agent to this game. An agent may be a user interface,
        an AI player, or anything that wants to receive events from the game
        and potentially send actions to it.

        Returns a value which can be passed to game.detachAgent() to detach this
        agent.
        '''
        f = AgentFilter()
        f.gameEvents.connectPlug(self._outPlug)
        f.agentEvents.connectPlug(eventPlug)
        f.agentRequests.connectPlug(controller)
        f.gameRequests.connectPlug(self._inPlug)

        return f

    def addAI(self, aiName='alpha', team=None):
        ai = makeAIAgent(self.world, aiName)
        self.addAgent(ai.eventPlug, ai.requestPlug)

        if team is not None:
            team = self.world.teams[team]
        ai.start(team)
        return ai

    def detachAgent(self, f):
        f.agentRequests.disconnectAll()
        f.agentEvents.disconnectAll()
        f.disconnect()
        f.gameEvents.disconnectAll()
        f.gameRequests.disconnectAll()

    def setGameMode(self, gameMode):
        if self.world.physics.hasMode(gameMode):
            self.world.eventPlug.send(SetGameModeMsg(gameMode.encode()))
            return True
        return False

    def setSpeed(self, gameSpeed):
        self.world.eventPlug.send(SetGameSpeedMsg(gameSpeed))

    def kickPlayer(self, playerId):
        self.world.eventPlug.send(RemovePlayerMsg(playerId))

    def endGame(self, team):
        if team == 'blue':
            self.world.eventPlug.send(GameOverMsg(self.world.teams[0].id,
                    False))
        elif team == 'red':
            self.world.eventPlug.send(GameOverMsg(self.world.teams[1].id,
                    False))
        elif team == 'draw':
            self.world.eventPlug.send(GameOverMsg('\x00', False))

    def startGame(self):
        self.world.eventPlug.send(GameStartMsg(self.world.gameDuration))

    def giveUpgrade(self, player, upgradeCode):
        self.world.eventPlug.send(PlayerHasUpgradeMsg(player.id, upgradeCode))

    def getPlayers(self):
        '''
        Returns a mapping of player name to player object.
        '''
        return dict((p.nick, p) for p in self.world.players)

    def reset(self, halfMapWidth=None, mapHeight=None, gameDuration=None):
        if halfMapWidth is None:
            halfMapWidth = self.world.map.layout.halfMapWidth
        if mapHeight is None:
            mapHeight = self.world.map.layout.mapHeight
        layout = self.layoutDatabase.generateRandomMapLayout(halfMapWidth,
                mapHeight)
        self.world.reset(layout, gameDuration)

    def setTeamName(self, teamNumber, teamName):
        try:
            team = self.world.teams[teamNumber]
        except KeyError:
            return
        self.world.eventPlug.send(SetTeamNameMsg(team.id, teamName.encode()))

    def getGameState(self):
        currentGameState = self.world.gameState
        if currentGameState in (GameState.PreGame, GameState.Starting):
            return 'P'
        if currentGameState == GameState.InProgress:
            return 'I'
        if currentGameState != GameState.Ended:
            return '?'

        winningTeam = self.world.winningTeam
        if winningTeam is None:
            return 'D'
        if winningTeam.id < winningTeam.opposingTeam.id:
            return 'B'
        return 'R'

    def getOrbCounts(self):
        return (
            self.world.teams[0].numOrbsOwned,
            self.world.teams[1].numOrbsOwned
        )

    def getTeamNames(self):
        return (
            self.world.teams[0].teamName,
            self.world.teams[1].teamName
        )

    def getGameMode(self):
        return self.world.gameMode

    def stop(self):
        if self.gameRecorder is not None:
            self.gameRecorder.stop()
        if self.aiInjector is not None:
            self.aiInjector.stop()

class QueryableGame(Game):
    '''
    Represents a game which may be queried about its state by agents. This is
    used for network servers so that the client universe can be updated to
    reflect the server universe.
    '''

    def __init__(self, world, outPlug, inPlug, gameRecorder, layoutDatabase,
            bootServer=False):
        Game.__init__(self, world, outPlug, inPlug, gameRecorder,
                bootServer=bootServer)
        self.layoutDatabase = layoutDatabase

    def addAgent(self, eventPlug, controller):
        wsr = WorldSettingsResponder(self.world, self.layoutDatabase)
        f = Game.addAgent(self, wsr.gameEvents, wsr.gameRequests)
        wsr.agentEvents.connectPlug(eventPlug)
        wsr.agentRequests.connectPlug(controller)

        return (f, wsr)

    def detachAgent(self, (f, wsr)):
        wsr.agentRequests.disconnectAll()
        wsr.agentEvents.disconnectAll()
        Game.detachAgent(self, f)

class IsolatedGame(Game):
    '''
    Used to encapsulate a game where we have no world, only streams of events
    (e.g. over the network). Behaves like a standard Game object, with the
    following additional attributes:
        .eventPlug, .requestPlug - plugs by which this game can communicate with
            the game it is mirroring.
        .syncWorld() - instructs this game to begin to syncronise its world with
            the remote world. Only call this method after eventPlug and
            requestPlug have been connected.
    '''
    def __init__(self, layoutDatabase):
        self._isolator = isolator = Isolator(layoutDatabase)
        Game.__init__(self, isolator.world, isolator.agentEvents,
                isolator.agentRequests, None)
        self.eventPlug = isolator.gameEvents
        self.requestPlug = isolator.gameRequests

    def syncWorld(self):
        self._isolator.begin()


class Alerter(object):
    '''
    Sends email alerts to a nominated email address.
    '''
    def __init__(self, settings):
        self.settings = settings

    def send(self, event, message):
        if self.settings is None or self.settings.recipientAddress is None:
            return
        alertSetting = getattr(self.settings, 'alertOn%s' % (event,))
        if not alertSetting:
            return

        from twisted.mail.smtp import sendmail

        msg = MIMEText(message)
        msg['Subject'] = self.settings.subject
        msg['From'] = sender = self.settings.senderAddress
        if isinstance(alertSetting, (str, unicode)):
            msg['To'] = recipient = alertSetting
        else:
            msg['To'] = recipient = self.settings.recipientAddress

        sendmail(self.settings.smtpServer, sender, [recipient], msg.as_string())

class AIInjector(object):
    def __init__(self, game, playerCount=6):
        self.game = game
        self.playerCount = playerCount
        self.loop = WeakLoopingCall(self, 'tick')
        self.loop.start(3, False)
        self.agents = []
        self.newAgents = set()
        self.aiNames = listAIs(playableOnly=True)

    def stop(self):
        self.loop.stop()

    def tick(self):
        self._graduateNewAgents()

        if self.game.world.gameState != GameState.Ended:
            self._stopAllAgents()
        else:
            self._adjustAgentsToTarget()

    def _graduateNewAgents(self):
        for agent in list(self.newAgents):
            if agent.playerId is not None:
                self.agents.append(agent)
                self.newAgents.remove(agent)

    def _stopAllAgents(self):
        if len(self.agents) != 0:
            log.info('AIInjector: Stopping all agents')
        for agent in self.agents:
            agent.stop()
            try:
                self.game.kickPlayer(agent.playerId)
            except Exception, e:
                log.exception(str(e))
        self.agents = []

    def _adjustAgentsToTarget(self):
        worldPlayers = len(self.game.world.players)
        newAgents = len(self.newAgents)
        if self.playerCount > worldPlayers + newAgents:
            self._addAgents(self.playerCount - worldPlayers - newAgents)
        else:
            self._removeAgents(worldPlayers + newAgents - self.playerCount)

    def _addAgents(self, count):
        log.info('AIInjector: Adding %d agents', count)
        for i in xrange(count):
            self.newAgents.add(self.game.addAI(random.choice(self.aiNames)))

    def _removeAgents(self, count):
        if count != 0:
            log.info('AIInjector: Removing %d agents', count)
        for i in xrange(count):
            if len(self.agents) == 0:
                break
            agent = self.agents.pop(0)
            agent.stop()
            self.game.kickPlayer(agent.playerId)

