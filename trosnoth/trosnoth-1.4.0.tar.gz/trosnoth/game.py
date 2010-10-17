# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2010 Joshua D Bartlett
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
from trosnoth.model.universe import Universe
from trosnoth.model.idmanager import IdManager
from trosnoth.model.validator import Validator
from trosnoth.model.agentfilter import AgentFilter
from trosnoth.model.universe_base import GameState
from trosnoth.model.isolator import Isolator, WorldSettingsResponder
from trosnoth.messages import (SetTeamNameMsg, GameStartMsg, GameOverMsg,
        SetGameModeMsg, RemovePlayerMsg)
from trosnoth.gamerecording.gamerecorder import makeGameRecorder

def makeLocalGame(gameName, layoutDatabase, halfMapWidth, mapHeight, duration=0,
        maxPlayers=8, authTagManager=None, voting=False, alertSettings=None):
    '''
    Makes and returns a local game.
    layoutDatabase may be a LayoutDatabase, or None. If None, the game will not
    be queryable by remote games.
    '''
    alerter = Alerter(alertSettings)
    idManager = IdManager()
    world = Universe(gameDuration=duration, authTagManager=authTagManager,
            voting=voting, layoutDatabase=layoutDatabase, gameName=gameName)
    validator = Validator(world, maxPlayers, authTagManager, alerter=alerter)

    world.eventPlug.connectPlug(idManager.inPlug)
    world.orderPlug.connectPlug(idManager.outPlug)
    validator.gameRequests.connectPlug(idManager.inPlug)
    validator.gameEvents.connectPlug(idManager.outPlug)

    gameRecorder = makeGameRecorder(world, layoutDatabase, idManager)

    if layoutDatabase is None:
        game = Game(world, validator.agentEvents, validator.agentRequests, gameRecorder)
    else:
        game = QueryableGame(world, validator.agentEvents, validator.agentRequests, gameRecorder,
            layoutDatabase)
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
    def __init__(self, world, outPlug, inPlug, gameRecorder):
        self.world = world
        self._outPlug = outPlug
        self._inPlug = inPlug
        self.gameRecorder = gameRecorder

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
        self.world.setGameSpeed(gameSpeed)

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

class QueryableGame(Game):
    '''
    Represents a game which may be queried about its state by agents. This is
    used for network servers so that the client universe can be updated to
    reflect the server universe.
    '''

    def __init__(self, world, outPlug, inPlug, gameRecorder, layoutDatabase):
        Game.__init__(self, world, outPlug, inPlug, gameRecorder)
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
        if not getattr(self.settings, 'alertOn%s' % (event,)):
            return

        from twisted.mail.smtp import sendmail

        msg = MIMEText(message)
        msg['Subject'] = self.settings.subject
        msg['From'] = sender = self.settings.senderAddress
        msg['To'] = recipient = self.settings.recipientAddress

        sendmail(self.settings.smtpServer, sender, [recipient], msg.as_string())
