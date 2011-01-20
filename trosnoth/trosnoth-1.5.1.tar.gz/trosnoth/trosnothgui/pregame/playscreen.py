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

import logging

import pygame

from trosnoth.gui.common import (Region, Canvas, Location, ScaledSize)
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.framework import framework, prompt
from trosnoth.gui.framework.dialogbox import DialogBox, OkBox
from trosnoth.gui.framework.elements import (SolidRect, TextButton)
from trosnoth.gui.framework.tabContainer import TabContainer
from trosnoth.gui.framework.tab import Tab
from trosnoth.network.lobby import (Lobby, AuthenticationCancelled,
        IncorrectServerVersion)
from trosnoth.network import authcommands
from trosnoth.network.client import ConnectionFailed
from trosnoth.utils.event import Event
from trosnoth.utils.twist import WeakCallLater
import trosnoth.version
from twisted.internet import defer
from twisted.internet.error import ConnectError
from twisted.protocols import amp

KNOWN_SERVERS = [
    'self',     # This instance of Trosnoth.
    ('localhost', 6787),
]
if trosnoth.version.release:
    KNOWN_SERVERS.append(('play.trosnoth.org', 6787))

KNOWN_SERVERS.extend([
    'others',   # Other games known by servers.
    'lan',      # LAN games.
    'create',   # Create a game on servers.
])

log = logging.getLogger('playscreen')

class PlayAuthScreen(framework.CompoundElement):
    def __init__(self, app, onSucceed=None, onFail=None):
        super(PlayAuthScreen, self).__init__(app)
        self.onSucceed = Event(onSucceed)
        self.onFail = Event(onFail)

        if app.displaySettings.useAlpha:
            alpha = 192
        else:
            alpha = None
        bg = SolidRect(app, app.theme.colours.playMenu, alpha,
                Region(centre=Canvas(512, 384), size=Canvas(924, 500)))

        colour = app.theme.colours.mainMenuColour
        font = app.screenManager.fonts.consoleFont
        self.logBox = LogBox(app, Region(size=Canvas(900, 425),
                midtop=Canvas(512, 146)), colour, font)

        font = app.screenManager.fonts.bigMenuFont
        cancel = TextButton(app, Location(Canvas(512, 624), 'midbottom'),
                'Cancel', font, app.theme.colours.secondMenuColour,
                app.theme.colours.white, onClick=self.cancel)
        self.cancelled = False
        self.elements = [bg, self.logBox, cancel]
        self.passwordGetter = None

    def _makePasswordGetter(self):
        if self.passwordGetter is None:
            self.passwordGetter = PasswordGUI(self.app)
        return self.passwordGetter

    @defer.deferredGenerator
    def begin(self, servers=None, canHost=True):
        self.cancelled = False
        self._makePasswordGetter().cancelled = False
        lobby = Lobby(self.app, self.app.netman)
        if servers is None:
            servers = list(KNOWN_SERVERS)

        badServers = set()

        for server in servers:
            if self.cancelled:
                break

            if server == 'self':
                if self.app.server is not None:
                    self.onSucceed.execute()
                    self.app.interface.connectToLocalServer()
                    return
            elif isinstance(server, tuple):
                if server in badServers:
                    continue
                self.logBox.log('Requesting games from %s:%d...' % server)
                try:
                   games = defer.waitForDeferred(lobby.getGames(server))
                   yield games
                   games = games.getResult()
                except ConnectError:
                    self.logBox.log('Unable to connect.')
                    badServers.add(server)
                except amp.UnknownRemoteError:
                    self.logBox.log('Error on remote server.')
                except amp.RemoteAmpError, e:
                    self.logBox.log('Error on remote server.')
                    log.exception(str(e))
                except IOError, e:
                    self.logBox.log('Error connecting to remote server.')
                    log.exception(str(e))
                    badServers.add(server)
                else:
                    if len(games) > 0:
                        for game in games:
                            try:
                                self.logBox.log('Found game: joining.')
                                result = defer.waitForDeferred(game.join(
                                        self._makePasswordGetter()))
                                yield result
                                result = result.getResult()
                            except authcommands.GameDoesNotExist:
                                pass
                            except AuthenticationCancelled:
                                pass
                            except authcommands.NotAuthenticated:
                                self.logBox.log('Authentication failure.')
                            except amp.UnknownRemoteError:
                                self.logBox.log('Error on remote server.')
                            except amp.RemoteAmpError, e:
                                self.logBox.log('Error on remote server.')
                                log.exception(str(e))
                            else:
                                self._joined(result)
                                return
                    else:
                        self.logBox.log('No running games.')
            elif server == 'others':
                for server in servers:
                    if server in badServers or not isinstance(server, tuple):
                        continue
                    self.logBox.log('Asking %s:%d about other games...' %
                            server)
                    try:
                        games = defer.waitForDeferred(lobby.getOtherGames(
                            server))
                        yield games
                        games = games.getResult()
                    except ConnectError:
                        self.logBox.log('Unable to connect.')
                        badServers.add(server)
                    else:
                        for game in games:
                            try:
                                self.logBox.log('Found game: joining.')
                                result = defer.waitForDeferred(game.join(
                                        self._makePasswordGetter()))
                                yield result
                                result = result.getResult()
                            except authcommands.GameDoesNotExist:
                                pass
                            except amp.UnknownRemoteError:
                                self.logBox.log('Error on remote server.')
                            except amp.RemoteAmpError, e:
                                self.logBox.log('Error on remote server.')
                                log.exception(str(e))
                            except IOError, e:
                                self.logBox.log(
                                        'Error connecting to remote server.')
                                log.exception(str(e))
                            except ConnectionFailed:
                                self.logBox.log('Could not connect.')
                            else:
                                self._joined(result)
                                return
            elif server == 'lan':
                self.logBox.log('Asking local network for other games...')
                games = defer.waitForDeferred(lobby.getMulticastGames())
                yield games
                games = games.getResult()
                for game in games:
                    try:
                        self.logBox.log('Found game: joining.')
                        result = defer.waitForDeferred(game.join(
                                self._makePasswordGetter()))
                        yield result
                        result = result.getResult()
                    except authcommands.GameDoesNotExist:
                        pass
                    except amp.UnknownRemoteError:
                        self.logBox.log('Error on remote server.')
                    except amp.RemoteAmpError, e:
                        self.logBox.log('Error on remote server.')
                        log.exception(str(e))
                    except IOError, e:
                        self.logBox.log('Error connecting to remote server.')
                        log.exception(str(e))
                    except ConnectionFailed:
                        self.logBox.log('Could not connect.')
                    else:
                        self._joined(result)
                        return
            elif server == 'create':
                for server in servers:
                    if server in badServers or not isinstance(server, tuple):
                        continue
                    self.logBox.log('Asking to create game on %s...' %
                            (server[0],))
                    try:
                       result = defer.waitForDeferred(lobby.startGame(server,
                               self._makePasswordGetter()))
                       yield result
                       result = result.getResult()
                    except ConnectError:
                        self.logBox.log('Unable to connect.')
                        badServers.add(server)
                    except authcommands.CannotCreateGame:
                        self.logBox.log('Server will not create game.')
                    except IncorrectServerVersion:
                        self.logBox.log('Wrong server version to create games.')
                    except AuthenticationCancelled:
                        pass
                    except authcommands.NotAuthenticated:
                        self.logBox.log('Authentication failure.')
                    except authcommands.GameDoesNotExist:
                        self.logBox.log(
                                'Error connecting to newly-created game.')
                    except amp.UnknownRemoteError:
                        self.logBox.log('Error on remote server.')
                    except amp.RemoteAmpError, e:
                        self.logBox.log('Error on remote server.')
                        log.exception(str(e))
                    except IOError, e:
                        self.logBox.log('Error connecting to remote server.')
                        log.exception(str(e))
                    else:
                        self.logBox.log('Game created and joined.')
                        self._joined(result)
                        return

        if canHost:
            if not self.cancelled:
                result = defer.waitForDeferred(HostGameQuery(self.app).run())
                yield result
                result = result.getResult()

                if not result:
                    self.onFail.execute()
                    return

                nick = self.app.identitySettings.nick
                if nick is not None:
                    serverName = "%s's game" % (nick,)
                else:
                    serverName = 'A Trosnoth game'
                self.app.startServer(serverName, 2, 1)

                # Notify remaining auth servers of this game.
                for server in servers:
                    if server in badServers or not isinstance(server, tuple):
                        continue
                    self.logBox.log('Registering game with %s...' %
                            (server[0],))
                    try:
                       result = defer.waitForDeferred(lobby.registerGame(server,
                               self.app.server))
                       yield result
                       result = result.getResult()
                    except ConnectError:
                        self.logBox.log('Unable to connect.')
                    if not result:
                        self.logBox.log('Registration failed.')

                self.onSucceed.execute()
                self.app.interface.connectToLocalServer()
        else:
            if not self.cancelled:
                box = OkBox(self.app, ScaledSize(450, 150), 'Trosnoth',
                        'Connecting unsuccessful.')
                box.onClose.addListener(self.onFail.execute)
                box.show()

    def _joined(self, result):
        netHandler, authTag = result
        self.onSucceed.execute()
        self.app.interface.connectedToGame(netHandler, authTag)

    def cancel(self, element):
        self.cancelled = True
        self._makePasswordGetter().cancelled = True
        self.onFail.execute()

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.onFail.execute()
        else:
            return super(PlayAuthScreen, self).processEvent(event)

class LogBox(framework.Element):
    '''
    Draws a canvas and adds text to the bottom of it, scrolling the canvas
    upwards.
    '''
    def __init__(self, app, region, colour, font):
        super(LogBox, self).__init__(app)
        self.image = None
        self.region = region
        self.colour = colour
        self.font = font

    def draw(self, screen):
        r = self.region.getRect(self.app)
        if self.image is not None:
            screen.blit(self.image, r.topleft)

    def log(self, text):
        t = self.font.render(self.app, text, False, self.colour,
                (255, 255, 255))
        t.set_colorkey((255, 255, 255))
        r = self.region.getRect(self.app)
        img = pygame.Surface(r.size)
        img.fill((255, 255, 255))
        img.set_colorkey((255, 255, 255))
        h = t.get_rect().height
        r.topleft = (0, h)
        if self.image is not None:
            img.blit(self.image, (0, 0), r)
        img.blit(t, (0, r.height - h))
        self.image = img

class PasswordGUIError(Exception):
    pass

class HostGameQuery(DialogBox):
    def __init__(self, app):
        size = Canvas(384, 150)
        DialogBox.__init__(self, app, size, 'Host game?')
        self._deferred = None

        font = app.screenManager.fonts.defaultTextBoxFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        labelColour = app.theme.colours.dialogBoxTextColour
        btnFont = app.screenManager.fonts.bigMenuFont

        self.elements = [
            TextElement(app, 'No games found. Host a game?', font,
                Location(self.Relative(0.5, 0.4), 'center'), labelColour),

            TextButton(app,
                Location(self.Relative(0.3, 0.85), 'center'),
                'Yes', btnFont, btnColour, highlightColour,
                onClick=self.yesClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.85), 'center'),
                'No', btnFont, btnColour, highlightColour,
                onClick=self.noClicked),
        ]

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_KP_ENTER, pygame.K_RETURN):
                self.yesClicked()
                return None
            elif event.key == pygame.K_ESCAPE:
                self.noClicked()
                return None
        else:
            return DialogBox.processEvent(self, event)

    def yesClicked(self, element=None):
        self.close()
        self._deferred.callback(True)

    def noClicked(self, element=None):
        self.close()
        self._deferred.callback(False)

    def run(self):
        if self.showing:
            raise PasswordGUIError('HostGameQuery already showing')
        self.show()
        result = self._deferred = defer.Deferred()
        return result

class PasswordGUI(DialogBox):
    def __init__(self, app):
        size = Canvas(512, 384)
        DialogBox.__init__(self, app, size, 'Please authenticate')
        self._deferred = None
        self._host = None

        font = app.screenManager.fonts.defaultTextBoxFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        errorTextColour = app.theme.colours.errorColour

        self.tabContainer = TabContainer(app,
                Region(topleft=self.Relative(0, 0),
                size=self.Relative(1, 0.75)), font,
                app.theme.colours.tabContainerColour)
        self.tabContainer.addTab(LoginTab(app))
        self.tabContainer.addTab(CreateAccountTab(app))

        self.errorText = TextElement(app, '', font,
            Location(self.Relative(0.5, 0.8), 'center'), errorTextColour)

        font = app.screenManager.fonts.bigMenuFont
        self.elements = [
            self.tabContainer,
            self.errorText,
            TextButton(app,
                Location(self.Relative(0.3, 0.9), 'center'),
                'Ok', font, btnColour, highlightColour,
                onClick=self.okClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.9), 'center'),
                'Cancel', font, btnColour, highlightColour,
                onClick=self.cancelClicked),
        ]
        self.cancelled = False

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_KP_ENTER,
                pygame.K_RETURN):
            self.okClicked()
            return None
        else:
            return DialogBox.processEvent(self, event)

    def cancelClicked(self, element=None):
        self.close()
        self._deferred.callback(None)

    def okClicked(self, element=None):
        if self.tabContainer.selectedIndex == 1:
            create = True
            # Check that passwords match.
            tab = self.tabContainer.tabs[1]
            if tab.passwordField.value != tab.passwordField2.value:
                self.setErrorText('Passwords do not match!')
                return
        else:
            create = False
            tab = self.tabContainer.tabs[0]

        username = tab.usernameField.value
        password = tab.passwordField.value

        if len(username) == 0:
            self.setErrorText('You must give a username!')
            return
        if len(password) == 0:
            self.setErrorText('Password cannot be blank!')
            return

        self.close()
        self.app.identitySettings.usernames[self._host] = username
        self._deferred.callback((create, username, password))

    def getPassword(self, host, errorMsg=''):
        if self.showing:
            raise PasswordGUIError('PasswordGUI already showing')
        if self.cancelled:
            self.cancelled = False
            result = self._deferred = defer.Deferred()
            WeakCallLater(0.1, result, 'callback', None)
            return result
        self.setCaption(host)
        self.tabContainer.tabs[0].reset(host)
        self.tabContainer.tabs[1].reset()
        self.setErrorText(errorMsg)
        self.show()
        self._host = host
        result = self._deferred = defer.Deferred()
        return result

    def setErrorText(self, text):
        self.errorText.setText(text)

class LoginTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app):
        Tab.__init__(self, app, 'Sign in')
        framework.TabFriendlyCompoundElement.__init__(self, app)
        font = app.screenManager.fonts.defaultTextBoxFont
        labelColour = app.theme.colours.dialogBoxTextColour
        inputColour = app.theme.colours.grey

        self.usernameField = prompt.InputBox(app,
            Region(topleft=self.Relative(0.1, 0.16),
                bottomright=self.Relative(0.9, 0.32)),
                font=font, colour=inputColour,
                validator=usernameValidator,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField = prompt.PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.48),
                bottomright=self.Relative(0.9, 0.64)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.elements = [
            TextElement(app, 'Username', font,
                Location(self.Relative(0.1, 0.11), 'midleft'),
                labelColour),
            self.usernameField,
            TextElement(app, 'Password', font,
                Location(self.Relative(0.1, 0.43), 'midleft'),
                labelColour),
            self.passwordField,
        ]
        self.tabOrder = [self.usernameField, self.passwordField]

    def reset(self, host):
        self.passwordField.setValue('')
        self.setFocus(self.passwordField)

        if self.usernameField.value == '':
            username = self.app.identitySettings.usernames.get(host)
            if username is None:
                self.setFocus(self.usernameField)
            else:
                self.usernameField.setValue(username)

class CreateAccountTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app):
        Tab.__init__(self, app, 'New account')
        framework.TabFriendlyCompoundElement.__init__(self, app)
        font = app.screenManager.fonts.defaultTextBoxFont
        labelColour = app.theme.colours.dialogBoxTextColour
        inputColour = app.theme.colours.grey

        self.usernameField = prompt.InputBox(app,
            Region(topleft=self.Relative(0.1, 0.16),
                bottomright=self.Relative(0.9, 0.32)),
                font=font, colour=inputColour,
                validator=usernameValidator,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField = prompt.PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.48),
                bottomright=self.Relative(0.9, 0.64)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField2 = prompt.PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.8),
                bottomright=self.Relative(0.9, 0.96)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.elements = [
            TextElement(app, 'Username', font,
                Location(self.Relative(0.1, 0.11), 'midleft'),
                labelColour),
            self.usernameField,
            TextElement(app, 'Password', font,
                Location(self.Relative(0.1, 0.43), 'midleft'),
                labelColour),
            self.passwordField,
            TextElement(app, 'Retype password', font,
                Location(self.Relative(0.1, 0.75), 'midleft'),
                labelColour),
            self.passwordField2,
        ]
        self.tabOrder = [self.usernameField, self.passwordField,
                self.passwordField2]

    def reset(self):
        self.passwordField.setValue('')
        self.passwordField2.setValue('')
        self.setFocus(self.usernameField)


USERNAME_CHARS = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789')
def usernameValidator(char):
    return char in USERNAME_CHARS
