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

from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.common import Location, FullScreenAttachedPoint, ScaledSize, Area
from trosnoth.src.gui.framework.unobtrusiveValueGetter import YesNoGetter

from trosnoth.src.trosnothgui.ingame.messagebank import MessageBank
from trosnoth.src.trosnothgui.ingame.stars import StarGroup
from trosnoth.src.trosnothgui.ingame.udpnotify import UDPNotificationBar
from trosnoth.src.trosnothgui.ingame import mainMenu
from trosnoth.src.trosnothgui.ingame.gauges import TurretGauge, RespawnGauge, UpgradeGauge
from trosnoth.src.trosnothgui.pregame.settingsMenu import SettingsMenu

from trosnoth.src.base import MenuError
from trosnoth.src.model.upgrades import Turret, Shield, MinimapDisruption, PhaseShift, Grenade, Ricochet
from trosnoth.src.model.team import Team
from trosnoth.src.model.player import Player

from trosnoth.src.messages import (
        BuyUpgradeMsg, DeleteUpgradeMsg, SetCaptainMsg,
        TeamIsReadyMsg, RespawnRequestMsg)

class DetailsInterface(framework.CompoundElement):
    '''Interface containing all the overlays onto the screen:
    chat messages, player lists, gauges, stars, etc.'''
    def __init__(self, app, gameInterface):
        super(DetailsInterface, self).__init__(app)
        world = gameInterface.world
        self.gameInterface = gameInterface

        # Maximum number of messages viewable at any one time
        maxView = 8

        self.world = world
        self.player = None
        self.currentMessages = MessageBank(self.app, maxView, 50,
                                           Location(FullScreenAttachedPoint(ScaledSize(-40,-40),'bottomright'), 'bottomright'),
                                           'right', 'bottom',
                                           self.app.screenManager.fonts.messageFont)
        self.currentChats = MessageBank(self.app, maxView, 50, Location(FullScreenAttachedPoint(ScaledSize(40,256),'topleft'), 'topleft'), 'left', 'top',
                                        self.app.screenManager.fonts.messageFont)
        # If we want to keep a record of all messages and their senders
        self.input = None
        self.inputText = None
        self.unobtrusiveGetter = None
        self.turretGauge = None
        self.respawnGauge = None
        self.upgradeGauge = None
        self.starGroup = StarGroup(self.app)
        self.udpNotifier = UDPNotificationBar(self.app)
        self.settingsMenu = SettingsMenu(app, onClose=self.hideSettings, showThemes=False)

        menuloc = Location(FullScreenAttachedPoint((0,0), 'bottomleft'), 'bottomleft')
        self.menuManager = mainMenu.MainMenu(self.app, menuloc, self, self.gameInterface.keyMapping)
        self.elements = [self.currentMessages, self.currentChats,
                         self.starGroup, self.udpNotifier]

    @property
    def controller(self):
        return self.gameInterface.controller

    def tick(self, deltaT):
        super(DetailsInterface, self).tick(deltaT)
        player = self.player
        if player is None:
            return
        self._updateTurretGauge()
        self._updateRespawnGauge()
        self._updateUpgradeGauge()

    def _updateTurretGauge(self):
        player = self.player
        if self.turretGauge is None:
            if player.turret:
                self.turretGauge = TurretGauge(self.app, Area(
                        FullScreenAttachedPoint(ScaledSize(0,-60),
                        'midbottom'), ScaledSize(100,30), 'midbottom'),
                        player)
                self.elements.append(self.turretGauge)
        elif not player.turret:
            self.elements.remove(self.turretGauge)
            self.turretGauge = None
            
    def _updateRespawnGauge(self):
        player = self.player
        if self.respawnGauge is None:
            if player.ghost:
                self.respawnGauge = RespawnGauge(self.app, Area(
                        FullScreenAttachedPoint(ScaledSize(0,-20),
                        'midbottom'), ScaledSize(100,30), 'midbottom'),
                        player)
                self.elements.append(self.respawnGauge)
        elif not player.ghost:
            self.elements.remove(self.respawnGauge)
            self.respawnGauge = None
            
    def _updateUpgradeGauge(self):
        player = self.player
        if self.upgradeGauge is None:
            if player.upgrade is not None:
                self.upgradeGauge = UpgradeGauge(self.app, Area(
                        FullScreenAttachedPoint(ScaledSize(0,-20),
                        'midbottom'), ScaledSize(100,30), 'midbottom'),
                        player)
                self.elements.append(self.upgradeGauge)
        elif player.upgrade is None:
            self.elements.remove(self.upgradeGauge)
            self.upgradeGauge = None

    def gameOver(self, winningTeam):
        self.gameInterface.gameOver(winningTeam)

    def setPlayer(self, player):
        self.player = player
        if self.menuManager not in self.elements:
            self.elements.append(self.menuManager)

    def showSettings(self):
        if self.settingsMenu not in self.elements:
            self.elements.append(self.settingsMenu)

    def hideSettings(self):
        if self.settingsMenu in self.elements:
            self.elements.remove(self.settingsMenu)
            self.gameInterface.updateKeyMapping()

    def _requestUpgrade(self, upgradeType):
        self.controller.send(BuyUpgradeMsg(self.player.id,
                upgradeType.upgradeType, random.randrange(1<<32)))

    def doAction(self, action):
        '''
        Activated by hotkey or menu.
        action corresponds to the action name in the keyMapping.
        '''
        if action == 'leaderboard':
            self.showPlayerDetails()
            self.menuManager.manager.reset()
        elif action == 'toggle interface':
            self.toggleInterface()
            self.menuManager.manager.reset()
        elif action == 'more actions':
            if self.menuManager is not None:
                self.menuManager.showMoreMenu()
        elif action == 'settings':
            self.showSettings()
        elif action == 'leave':
            # Disconnect from the server.
            self.gameInterface.disconnect()
        elif action == 'menu':
            # Return to main menu and show or hide the menu.
            if self.menuManager is not None:
                self.menuManager.escape()
        elif action == 'follow':
            if self.gameInterface.world.replay:
                # Replay-specific: follow the action.
                self.gameInterface.gameViewer.setTarget(None)
        elif action == 'toggle terminal':
            self.gameInterface.toggleTerminal()

        # All actions after this line should require a player.
        if self.player is None:
            return
        if action == 'respawn':
            self.controller.send(RespawnRequestMsg(self.player.id,
                    random.randrange(1<<32)))
        elif action == 'turret':
            self._requestUpgrade(Turret)
            self.menuManager.manager.reset()
        elif action == 'shield':
            self._requestUpgrade(Shield)
            self.menuManager.manager.reset()
        elif action == 'minimap disruption':
            self._requestUpgrade(MinimapDisruption)
            self.menuManager.manager.reset()
        elif action == 'phase shift':
            self._requestUpgrade(PhaseShift)
            self.menuManager.manager.reset()
        elif action == 'grenade':
            self._requestUpgrade(Grenade)
            self.menuManager.manager.reset()
        elif action == 'ricochet':
            self._requestUpgrade(Ricochet)
            self.menuManager.manager.reset()
        elif action == 'abandon':
            self.abandon(self.player)
            self.menuManager.manager.reset()
        elif action == 'chat':
            self.chat()
            self.menuManager.manager.reset()
        elif action == 'captain':
            self.becomeCaptain()
            self.menuManager.manager.reset()
        elif action == 'team ready':
            self.teamReady()
            self.menuManager.manager.reset()
        elif action == 'buy upgrade':
            if self.menuManager is not None:
                self.menuManager.showBuyMenu()

    def newMessage(self, text, colour=None):
        if colour is None:
            colour = self.app.theme.colours.grey
        self.currentMessages.newMessage(text, colour)

    def newChat(self, text, sender, private):
        if sender is self.player:
            # Don't bother receiving messages from myself.
            return

        nick = sender.nick
        if not private:
            # Message for everyone
            extra = ': '

        elif isinstance(private, Player) and self.player is private:
            # Destined for the one player
            extra = ' (private): '

        elif isinstance(private, Team) and self.player is not None and \
                self.player.team == private:
            # Destined for the one team.
            extra = ': '

        else:
            # May not have been destined for our player after all.
            print "Don't want this text"
            return
        allText = nick + extra + text
        self.currentChats.newMessage(allText,
                self.app.theme.colours.chatColour(sender.team))

    def sentPublicChat(self, team, text):
        self.currentChats.newMessage('Me (open): %s' % (text,),
                self.app.theme.colours.chatColour(team))

    def sentPrivateChat(self, team, nick, text):
        self.currentChats.newMessage('Me (to_%s): %s' % (nick, text),
                self.app.theme.colours.chatColour(team))

    def sentTeamChat(self, team, text):
        self.currentChats.newMessage('Me: %s' % (text,),
                self.app.theme.colours.chatColour(team))

    def processEvent(self, event):
        '''Event processing works in the following way:
        1. If there is a prompt on screen, the prompt will either use the
        event, or pass it on.
        2. If passed on, the event will be sent back to the main class, for it
        to process whether player movement uses this event. If it doesn't use
        the event, it will pass it back.
        3. If so, the hotkey manager will see if the event means anything to it.
        If not, that's the end, the event is ignored.'''

        try:
            return super(DetailsInterface, self).processEvent(event)
        except MenuError, err:
            self.newMessage(err.value, self.app.theme.colours.errorMessageColour)
            self.endInput()
            return None


    def endInput(self):
        if self.input:
            self.elements.remove(self.input)
            self.input = None
        if self.inputText:
            self.elements.remove(self.inputText)
            self.inputText = None
        if self.unobtrusiveGetter:
            self.elements.remove(self.unobtrusiveGetter)
            self.unobtrusiveGetter = None
        if self.menuManager is not None and self.menuManager not in self.elements:
            self.elements.append(self.menuManager)
        self.input = self.inputText = None


    def inputStarted(self):
        self.elements.append(self.input)
        self.elements.append(self.inputText)
        self.input.onEsc.addListener(lambda sender: self.endInput())
        self.input.onEnter.addListener(lambda sender: self.endInput())
        if self.menuManager is not None:
            try:
                self.elements.remove(self.menuManager)
            except ValueError:
                pass



    def chat(self):
        if not self.player:
            return

        self.gameInterface.gameViewer.openChat(self.player)


    def abandon(self, player):
        '''
        Called when a player says they wish to abandon their upgrade.
        '''
        if player.upgrade:
            addOn = 'upgrade'
            if player.upgrade.inUse and type(player.upgrade) == Grenade:
                self.newMessage('Cannot abandon an active grenade!',
                        self.app.theme.colours.errorMessageColour)
                raise MenuError, "Cannot abandon an active grenade!"

        else:
            return

        message = 'Really abandon your ' + addOn + ' (Y/N)'
        self.endInput()
        self.unobtrusiveGetter = YesNoGetter(self.app, Location(
                FullScreenAttachedPoint((0,0), 'center'), 'center'), message,
                self.app.screenManager.fonts.unobtrusivePromptFont,
                self.app.theme.colours.unobtrusivePromptColour, 3)
        self.elements.append(self.unobtrusiveGetter)

        def gotValue(abandon):
            if self.unobtrusiveGetter:
                self.elements.remove(self.unobtrusiveGetter)
                self.unobtrusiveGetter = None
            if abandon:
                self.controller.send(DeleteUpgradeMsg(player.id, player.upgrade.upgradeType))

        self.unobtrusiveGetter.onGotValue.addListener(gotValue)


    def upgradeUsed(self, player):
        upgrade = player.upgrade
        if upgrade is None:
            upgrade = 'an upgrade'
        else:
            upgrade = repr(upgrade)
        message = '%s is using %s' % (player.nick, player.upgrade)
        self.newMessage(message)

    def upgradeDestroyed(self, player, upgrade):
        if upgrade is None:
            upgrade = 'upgrade'
        else:
            upgrade = repr(upgrade)
        message = "%s's %s is gone" % (player.nick, upgrade)
        self.newMessage(message)

    def becomeCaptain(self):
        if self.player:
            self.controller.send(SetCaptainMsg(self.player.id))

    def teamReady(self):
        if self.player:
            self.controller.send(TeamIsReadyMsg(self.player.id))

    def showPlayerDetails(self):
        self.gameInterface.gameViewer.toggleLeaderBoard()

    def toggleInterface(self):
        self.gameInterface.gameViewer.toggleInterface()
