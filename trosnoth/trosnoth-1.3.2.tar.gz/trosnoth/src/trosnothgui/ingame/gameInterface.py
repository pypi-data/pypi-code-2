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

from trosnoth.src.gui.framework import framework, hotkey, console
from trosnoth.src.gui import keyboard
from trosnoth.src.gui.common import Region, Screen
from trosnoth.src.gui.screenManager.windowManager import MultiWindowException

from trosnoth.src.trosnothgui.ingame import viewManager
from trosnoth.src.trosnothgui.ingame.replayInterface import ReplayMenu, ViewControlInterface
from trosnoth.src.trosnothgui.ingame.gameMenu import GameMenu
from trosnoth.src.trosnothgui.ingame.detailsInterface import DetailsInterface
from trosnoth.src.trosnothgui.ingame.observerInterface import ObserverInterface
from trosnoth.src.trosnothgui.ingame.playerInterface import PlayerInterface
from trosnoth.src.trosnothgui.ingame.gameOverInterface import GameOverInterface

from trosnoth.src.base import MenuError
from trosnoth.src import keymap

from trosnoth.data import user, getPath

from trosnoth.src.utils.components import Component, Plug, handler

from trosnoth.src.model.universe import Abort

from trosnoth.src.utils.math import distance
from trosnoth.src.utils.event import Event

from trosnoth.src.model.upgrades import MinimapDisruption, Grenade
from trosnoth.src.messages import (TaggingZoneMsg, ChatFromServerMsg, ChatMsg,
        GameStartMsg, GameOverMsg, TeamIsReadyMsg, SetCaptainMsg,
        StartingSoonMsg, SetTeamNameMsg, SetGameModeMsg, ShotFiredMsg,
        KillShotMsg, RespawnMsg, CannotRespawnMsg, PlayerKilledMsg,
        PlayerUpdateMsg, PlayerHitMsg, JoinRequestMsg, JoinSuccessfulMsg,
        CannotJoinMsg, AddPlayerMsg, UpdatePlayerStateMsg, AimPlayerAtMsg,
        RemovePlayerMsg, PlayerHasUpgradeMsg, PlayerStarsSpentMsg,
        DeleteUpgradeMsg, CannotBuyUpgradeMsg, ConnectionLostMsg,
        NotifyUDPStatusMsg, ZoneStateMsg)

from twisted.internet import defer, reactor

class GameInterface(framework.CompoundElement, Component):
    '''Interface for when we are connected to a game.'''

    controller = Plug()
    eventPlug = Plug()

    def __init__(self, app, world, onDisconnectRequest=None,
            onConnectionLost=None):
        super(GameInterface, self).__init__(app)
        Component.__init__(self)

        self.onDisconnectRequest = Event()
        if onDisconnectRequest is not None:
            self.onDisconnectRequest.addListener(onDisconnectRequest)

        self.onConnectionLost = Event()
        if onConnectionLost is not None:
            self.onConnectionLost.addListener(onConnectionLost)
            
        self.world = world

        self.keyMapping = keyboard.KeyboardMapping(keymap.default_game_keys)
        self.updateKeyMapping()

        self.gameViewer = viewManager.GameViewer(self.app, self, world)
        if world.replay:
            self.gameMenu = ReplayMenu(self.app, world)
            closeReplay = self.onDisconnectRequest.execute
            self.gameMenu.onDisconnectRequest.addListener(closeReplay)
        else:
            self.gameMenu = GameMenu(self.app, self, world)
        self.detailsInterface = DetailsInterface(self.app, self)
        self.runningPlayerInterface = None
        self.observerInterface = ObserverInterface(self.app, self)
        self.menuHotkey = hotkey.MappingHotkey(self.app, 'menu', mapping=self.keyMapping)
        self.menuHotkey.onActivated.addListener(self.showMenu)
        self.elements = [
                         self.gameViewer, self.gameMenu,
                         self.menuHotkey, self.detailsInterface
                        ]
        self.hotkeys = hotkey.Hotkeys(self.app, self.keyMapping, self.detailsInterface.doAction)
        self.menuShowing = True
        self.gameOverScreen = None
        self.terminal = None

        self.joiningDeferred = None

        self.vcInterface = None
        if world.replay:
            self.vcInterface = ViewControlInterface(self.app, self)
            self.elements.append(self.vcInterface)
            self.hideMenu()


    @handler(SetTeamNameMsg, eventPlug)
    @handler(UpdatePlayerStateMsg, eventPlug)
    @handler(AimPlayerAtMsg, eventPlug)
    @handler(SetGameModeMsg, eventPlug)
    @handler(PlayerUpdateMsg, eventPlug)
    @handler(ZoneStateMsg, eventPlug)
    def ignoreMessage(self, msg):
        pass

    def updateKeyMapping(self):
        # Set up the keyboard mapping.
        try:
            # Try to load keyboard mappings from the user's personal settings.
            config = open(getPath(user, 'keymap'), 'rU').read()
            self.keyMapping.load(config)
        except IOError:
            pass

    @handler(ConnectionLostMsg, eventPlug)
    def connectionLost(self, msg):
        self.cleanUp()
        self.gameMenu.cleanUp()
        self.onConnectionLost.execute()

    def joined(self, player):
        '''Called when joining of game is successful.'''
        print 'Joined game ok.'
        playerSprite = self.gameViewer.worldgui.getPlayerSprite(player.id)
        self.runningPlayerInterface = pi = PlayerInterface(self.app, self, playerSprite)
        self.detailsInterface.setPlayer(player)
        self.elements = [self.gameViewer,
                         pi, self.menuHotkey, self.hotkeys, self.detailsInterface]

    def showMenu(self):
        if self.runningPlayerInterface is not None:
            if self.runningPlayerInterface.player is not None:
                # Can't get to this particular menu after you've joined the game.
                return
        self.elements = [self.gameViewer, self.gameMenu]
        self.menuShowing = True
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

    def hideMenu(self):
        if self.runningPlayerInterface is not None:
            self.elements = [self.gameViewer, self.runningPlayerInterface, self.gameMenu, self.menuHotkey,
                             self.hotkeys, self.detailsInterface]
        else:
            self.elements = [self.gameViewer, self.observerInterface, self.gameMenu, self.menuHotkey,
                             self.hotkeys, self.detailsInterface]
        if self.vcInterface is not None:
            self.elements.insert(2, self.vcInterface)

        if self.gameOverScreen:
            self.elements.append(self.gameOverScreen)
        self.menuShowing = False

    def toggleTerminal(self):
        if self.terminal is None:
            self.terminal = console.TrosnothInteractiveConsole(self.app,
                self.app.screenManager.fonts.consoleFont,
                Region(size=Screen(1, 0.4), bottomright=Screen(1, 1)),
                locals={'app': self.app})
            self.terminal.interact().addCallback(self._terminalQuit)

        from trosnoth.src.utils.utils import timeNow
        if self.terminal in self.elements:
            if timeNow() > self._termWaitTime:
                self.elements.remove(self.terminal)
        else:
            self._termWaitTime = timeNow() + 0.1
            self.elements.append(self.terminal)
            self.setFocus(self.terminal)

    def _terminalQuit(self, result):
        if self.terminal in self.elements:
            self.elements.remove(self.terminal)
        self.terminal = None

    def disconnect(self):
        self.cleanUp()
        self.onDisconnectRequest.execute()

    def joinGame(self, nick, team, timeout=5):
        result = defer.Deferred()
        if self.joiningDeferred is not None:
            result.errback(AssertionError('Already in process of joining.'))
            return result

        if team is None:
            teamId = '\x00'
        else:
            teamId = team.id

        self.controller.send(JoinRequestMsg(teamId, random.randrange(1<<32),
                nick.encode()))
        self.joiningDeferred = result
        reactor.callLater(timeout, self._joinTimedOut)

        return result

    @handler(JoinSuccessfulMsg, eventPlug)
    def joinedOk(self, msg):
        reactor.callLater(0, self._joinedOk, msg)

    def _joinedOk(self, msg):
        d = self.joiningDeferred
        if d is None:
            return

        try:
            player = self.world.playerWithId[msg.playerId]
        except KeyError:
            # Retry until the timeout cancels it.
            reactor.callLater(0.5, self._joinedOk, msg)
        else:
            d.callback(('success', player))
            self.joiningDeferred = None

    @handler(CannotJoinMsg, eventPlug)
    def joinFailed(self, msg):
        d = self.joiningDeferred
        if d is None:
            return
        r = msg.reasonId
        if r == 'F':
            d.callback(['full'])
        elif r == 'O':
            d.callback(['over'])
        elif r == 'W':
            d.callback(['wait', str(round(msg.waitTime, 1))])
        elif r == 'N':
            d.callback(['nick'])
        else:
            d.callback(['unknown reason code: %s' % (r,)])
        self.joiningDeferred = None

    def _joinTimedOut(self):
        if self.joiningDeferred is None:
            return
        self.joiningDeferred.callback(['timeout'])
        self.joiningDeferred = None

    def cleanUp(self):
        if self.gameViewer.timerBar is not None:
            self.gameViewer.timerBar.kill()
            self.gameViewer.timerBar = None
        try:
            self.gameViewer.closeChat()
        except MultiWindowException:
            pass

    def gameOver(self, winningTeam):
        self.gameOverScreen = GameOverInterface(self.app, winningTeam,
                self.disconnect)

        self.elements.append(self.gameOverScreen)
        try:
            self.elements.remove(self.menuHotkey)
        except:
            pass

    def reDraw(self):
        # TODO: This is redrawing every time there's a tag.
        # Could optimise that a bit to only redraw if the screen contains
        # one of its mapblocks.
        self.gameViewer.viewManager.reDraw()

    def processEvent(self, event):
        try:
            return super(GameInterface, self).processEvent(event)
        except MenuError, err:
            self.detailsInterface.newMessage(err.value,
                    self.app.theme.colours.errorMessageColour)
            self.detailsInterface.endInput()
            return None


    @handler(PlayerStarsSpentMsg, eventPlug)
    def discard(self, msg):
        pass

    @handler(AddPlayerMsg, eventPlug)
    def addPlayer(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s has joined %s' % (player.nick, player.team)
            self.detailsInterface.newMessage(message)
            self.gameViewer.worldgui.addPlayer(player)
        except Abort:
            pass

    @handler(RemovePlayerMsg, eventPlug)
    def removePlayer(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s has left the game' % (player.nick,)
            self.detailsInterface.newMessage(message)
            self.gameViewer.worldgui.removePlayer(player)
        except Abort:
            pass

    @handler(GameStartMsg, eventPlug)
    def gameStart(self, msg):
        message = 'The game is now on!!'
        self.detailsInterface.newMessage(message)
        if self.gameViewer.timerBar:
            self.gameViewer.timerBar.loop()
        #self.playSound('start', 1)

    @handler(GameOverMsg, eventPlug)
    def gameIsOver(self, msg):
        try:
            team = self.world.teamWithId[msg.teamId]
        except KeyError:
            team = None
        self.gameOver(team)
        if msg.timeOver:
            message2 = 'Game time limit has expired'
            self.detailsInterface.newMessage(message2)
        if self.gameViewer.timerBar:
            self.gameViewer.timerBar.gameFinished()
        #self.playSound('end', 1)

    @handler(SetCaptainMsg, eventPlug)
    def setCaptain(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            self.detailsInterface.newMessage("%s is %s's captain" %
                    (player.nick, player.team), self.getChatColour(player.team))
        except Abort:
            pass

    @handler(TeamIsReadyMsg, eventPlug)
    def teamIsReady(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            self.detailsInterface.newMessage('%s is ready' %
                    (player.team,), self.getChatColour(player.team))
        except Abort:
            pass

    def getChatColour(self, team):
        return self.app.theme.colours.chatColour(team)

    @handler(CannotBuyUpgradeMsg, eventPlug)
    def notEnoughStars(self, msg):
        if self.detailsInterface.player.id == msg.playerId:
            if msg.reasonId == 'N':
                text = 'Your team does not have enough stars.'
            elif msg.reasonId == 'A':
                text = 'You already have an upgrade.'
            elif msg.reasonId == 'D':
                text = 'You cannot buy an upgrade while dead.'
            elif msg.reasonId == 'P':
                text = 'You cannot buy an upgrade before the game starts.'
            elif msg.reasonId == 'T':
                text = 'There is already a turret in this zone.'
            elif msg.reasonId == 'E':
                text = 'You are too close to the zone edge.'
            elif msg.reasonId == 'O':
                text = 'You are too close to the orb.'
            elif msg.reasonId == 'F':
                text = 'You are not in a dark friendly zone.'
            elif msg.reasonId == 'M':
                text = 'Your team is already using a minimap disruption.'
            else:
                text = 'You cannot buy that upgrade at this time.'
            self.detailsInterface.newMessage(text)

    @handler(PlayerHasUpgradeMsg, eventPlug)
    def gotUpgrade(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            self.detailsInterface.upgradeUsed(player)
            upgrade = self.world.getUpgradeType(msg.upgradeType)
            if upgrade == MinimapDisruption:
                self.gameViewer.minimapDisruption(player)
            elif upgrade == Grenade:
                self.gameViewer.worldgui.addGrenade(player.upgrade.gr)
        except Abort:
            pass

    @handler(DeleteUpgradeMsg, eventPlug)
    def deleteUpgradeMsg(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            self.detailsInterface.upgradeDestroyed(player, player.upgrade)
            if isinstance(player.upgrade, MinimapDisruption) or msg.upgradeType == MinimapDisruption.upgradeType:
                self.gameViewer.endMinimapDisruption(player)
            elif isinstance(player.upgrade, Grenade):
                self.gameViewer.worldgui.removeGrenade(player.upgrade.gr)
        except Abort:
            print 'Unable to remove upgrade: %s' % (msg.playerId,)

    @handler(ChatFromServerMsg, eventPlug)
    def gotChatFromServer(self, msg):
        self.detailsInterface.newMessage(msg.text.decode())

    @handler(StartingSoonMsg, eventPlug)
    def startingSoon(self, msg):
        self.detailsInterface.newMessage('Both teams are ready. Game starting in %d seconds' % msg.delay)

    @handler(TaggingZoneMsg, eventPlug)
    def zoneTagged(self, msg):
        self.reDraw()
        try:
            zoneId = self.world.zoneWithId[msg.zoneId].id
        except KeyError:
            zoneId = '<?>'

        if msg.playerId == '\x00':
            message = 'Zone %s rendered neutral' % (zoneId,)
        else:
            try:
                player = self.world.playerWithId[msg.playerId]
            except KeyError:
                nick = '<?>'
            else:
                nick = player.nick
                # Draw a star.
                rect = self.gameViewer.worldgui.getPlayerSprite(player.id).rect
                self.detailsInterface.starGroup.star(rect.center)
            message = '%s tagged zone %s' % (nick, zoneId)

        self.detailsInterface.newMessage(message)
        #self.playSound('tag', 1)

    @handler(PlayerKilledMsg, eventPlug)
    def playerKilled(self, msg):
        try:
            target = self.world.getPlayer(msg.targetId)
            try:
                killer = self.world.playerWithId[msg.killerId]
            except KeyError:
                killer = None
                message = '%s was killed' % (target.nick,)
                self.detailsInterface.newMessage(message)
            else:
                message = '%s killed %s' % (killer.nick, target.nick)
                self.detailsInterface.newMessage(message)
                if (self.runningPlayerInterface is not None and
                        self.runningPlayerInterface.player == killer):
                    rect = self.gameViewer.worldgui.getPlayerSprite(target.id
                            ).rect
                    self.detailsInterface.starGroup.star(rect.center)
        except Abort:
            pass

    @handler(RespawnMsg, eventPlug)
    def playerRespawn(self, msg):
        try:
            player = self.world.getPlayer(msg.playerId)
            message = '%s is back in the game' % (player.nick,)
            self.detailsInterface.newMessage(message)
            #dist = self.distance(msg.player.pos)
            #self.playSound('respawn', self.getSoundVolume(dist))
        except Abort:
            pass

    @handler(CannotRespawnMsg, eventPlug)
    def respawnFailed(self, msg):
        if msg.reasonId == 'P':
            message = 'The game has not started yet.'
        elif msg.reasonId == 'A':
            message = 'You are already alive.'
        elif msg.reasonId == 'T':
            message = 'You cannot respawn yet.'
        elif msg.reasonId == 'E':
            message = 'Cannot respawn outside friendly zone.'
        else:
            message = 'You cannot respawn here.'
        self.detailsInterface.newMessage(message,
                self.app.theme.colours.errorMessageColour)

    def sendPrivateChat(self, player, targetId, text):
        self.controller.send(ChatMsg(player.id, 'p', targetId, text.encode()))
        try:
            nick = self.world.playerWithId[targetId].nick
        except KeyError:
            nick = '???'
        self.detailsInterface.sentPrivateChat(player.team, nick, text)

    def sendTeamChat(self, player, text):
        self.controller.send(ChatMsg(player.id, 't', player.team.id,
                text.encode()))
        self.detailsInterface.sentTeamChat(player.team, text)

    def sendPublicChat(self, player, text):
        self.controller.send(ChatMsg(player.id, 'o', '\x00', text.encode()))
        self.detailsInterface.sentPublicChat(player.team, text)

    @handler(ChatMsg, eventPlug)
    def chat(self, msg):
        try:
            sender = self.world.getPlayer(msg.playerId)
            if msg.kind == 't':
                target = self.world.getTeam(msg.targetId)
            elif msg.kind == 'p':
                target = self.world.getPlayer(msg.targetId)
            else:
                target = None
            self.detailsInterface.newChat(msg.text.decode(), sender, target)
            #self.playSound('chat', 1)
        except Abort:
            pass

    @handler(ShotFiredMsg, eventPlug)
    def shotFired(self, msg):
        shot = self.world.shotWithId(msg.playerId, msg.shotId)
        if shot is not None:
            self.gameViewer.worldgui.addShot(shot)
        #pos = msg.shot.pos
        #dist = self.distance(pos)
        #self.playSound('shoot', self.getSoundVolume(dist))

    @handler(PlayerHitMsg, eventPlug)
    @handler(KillShotMsg, eventPlug)
    def shotGone(self, msg):
        self.gameViewer.worldgui.removeShot(msg.shooterId, msg.shotId)

    @handler(NotifyUDPStatusMsg, eventPlug)
    def udpStatusChanged(self, msg):
        if msg.connected:
            self.detailsInterface.udpNotifier.hide()
        else:
            self.detailsInterface.udpNotifier.show()

    def distance(self, pos):
        return distance(self.gameViewer.viewManager.getTargetPoint(), pos)

    def getSoundVolume(self, distance):
        'The volume for something that far away from the player'
        # Up to 500px away is within the "full sound zone" - full sound
        distFromScreen = max(0, distance - 500)
        # 1000px away from "full sound zone" is 0 volume:
        return 1 - (distFromScreen / 1000)

    def playSound(self, action, volume=1):
        self.app.soundPlayer.play(action, volume)

